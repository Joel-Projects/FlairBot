import datetime
import logging
import sys
import time
from contextlib import contextmanager
from multiprocessing import Process

import praw
import requests
import timeago
from BotUtils.CommonUtils import BotServices, getBotSettings
from SpazUtils import Usernotes
from discord import embeds
from models import Flairlog, RemovalReason, Subreddit

from sqlalchemy import create_engine, sql
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, sessionmaker


thingTypes = {'t1': 'comment', 't4': 'message', 't2': 'redditor', 't3': 'submission', 't5': 'subreddit', 't6': 'trophy'}

class SessionManager:

    def __init__(self, session):
        self.session = session

    @contextmanager
    def startTransaction(self) -> Session:
        try:
            yield session.session
            session.session.commit()
        except:
            session.session.rollback()
            raise
        finally:
            session.session.close()

class FlairRemoval:

    def __init__(self, reddit, subreddit, webhook, log, slack=False, slackChannel=None, webhookEnabled=True, header=None, footer=None, session=None):
        """
        Initialized FlairRemoval Class

        :param reddit: reddit instance
        :param subreddit: subreddit object
        :param webhook: webhook url to send removal notifications can be discord or slack. If slack set slack params.
        :param sql: psycopg2 cursor object
        :param slack: set true to use slack
        :param slackChannel: channel for slack webhook

        """
        self.reddit = reddit
        self.subreddit = subreddit
        self.webhook = webhook
        self.slack = slack
        self.log = log
        self.slackChannel = slackChannel
        self.webhookEnabled = webhookEnabled
        self.header = header
        self.footer = footer
        self.session: Session = session
        self.sessionManager = SessionManager(session)

    def logStream(self):
        return praw.models.util.stream_generator(self.subreddit.mod.log, skip_existing=True, pause_after=0, attribute_name='id', action='editflair')

    def __parseModAction(self, action: praw.models.ModAction, flair: str):
        actionId = getattr(action, 'id', None).split('_')[1]
        created_utc = getattr(action, 'created_utc', None)
        moderator = getattr(action, '_mod', None)
        subreddit = getattr(action, 'subreddit', None)
        target_author = getattr(action, 'target_author', None)
        target_fullname = getattr(action, 'target_fullname', None)
        target_id = target_fullname.split('_')[1]
        target_body = getattr(action, 'target_body', None)
        target_permalink = getattr(action, 'target_permalink', None)
        target_title = getattr(action, 'target_title', None)
        data = {
            'id': actionId,
            'created_utc': datetime.datetime.fromtimestamp(created_utc).astimezone(),
            'moderator': moderator,
            'subreddit': subreddit,
            'target_author': target_author,
            'target_id': target_id,
            'target_body': target_body,
            'target_permalink': target_permalink,
            'target_title': target_title,
            'flair': flair
        }
        return data

    def __genDateString(self, epoch=time.localtime(), gmtime=False, format='%B %d, %Y at %I:%M:%S %p %Z'):
        if not gmtime:
            return time.strftime(format, time.localtime(epoch))
        else:
            return time.strftime(format, time.gmtime(epoch))

    def checkModAction(self, modAction: praw.models.ModAction):
        if modAction and modAction.action == 'editflair' and modAction.target_fullname and modAction.target_fullname[:2] == "t3":
            submission = self.reddit.submission(id=modAction.target_fullname[3:])
            try:
                if hasattr(submission, 'link_flair_text') and submission.link_flair_text:
                    submissionFlair = submission.link_flair_text.lower()
                else:
                    submissionFlair = ''
                data = self.__parseModAction(modAction, submissionFlair)
                self.log.debug('{self.subreddit.display_nameC | hecking if in flair list')
                actionParam = None
                try:
                    actionParam = self.session.query(RemovalReason).filter_by(subreddit=self.subreddit.display_name, flair_text=submissionFlair, enabled=True).first()
                except Exception as error:
                    self.log.exception(error)
                if actionParam:
                    self.log.info(f'{self.subreddit.display_name} | Found flair: {submissionFlair} by {modAction._mod} at {self.__genDateString(modAction.created_utc, format="%m/%d/%Y %I:%M:%S %p")}')
                    try:
                        self.log.info(f'{self.subreddit.display_name} | Checking if already actioned')
                        result = None
                        try:
                            statement = insert(Flairlog).values(**data).returning(sql.text('case when xmax::text::int > 0 then \'alreadyRemoved\' else \'inserted\' end,ctid'))
                            result = session.execute(statement.on_conflict_do_update(index_elements=['id'], set_=dict(created_utc=statement.excluded.created_utc))).fetchone()[0]
                        except Exception as error:
                            self.log.exception(error)
                            session.rollback()
                        if result == 'alreadyRemoved':
                            self.log.info(f'{self.subreddit.display_name} | Already Removed {submission.shortlink} by {getattr(submission.author, "name", "[deleted]")} with {submissionFlair} flair, Mod: {modAction._mod}')
                        else:
                            try:
                                self.log.info(f'{self.subreddit.display_name} | Removing')
                                self.__action(submission, actionParam, modAction)
                                self.log.info(
                                    f'{self.subreddit.display_name} | Successfully removed {submission.shortlink} by {getattr(submission.author, "name", "[deleted]")} with {submissionFlair} flair, Mod: {modAction._mod}')
                            except Exception as error:
                                self.log.exception(error)
                                pass
                    except Exception as error:
                        self.log.exception(error)
                        pass
            except Exception as error:
                self.log.exception(error)
                pass

    def __action(self, submission: praw.models.reddit.submission.Submission, action, modAction: praw.models.ModAction, testing=False):
        if not testing:
            try:
                submission.mod.remove()
                if action.ban:
                    self.__setBan(submission, action)
                if action.lock:
                    submission.mod.lock()
                if action.comment:
                    comment = submission.reply(self.__substituteToolboxTokens(action.comment, submission, self.header, self.footer))
                    comment.mod.distinguish(how='yes', sticky=True)
                    comment.mod.approve()
                    if action.lock_comment:
                        comment.mod.lock()
                if action.usernote:
                    self.__setUsernote(action, submission, modAction)
            except Exception as error:
                self.log.error(error)
        if self.webhookEnabled:
            if self.slack:
                data = self.__generateSlackEmbed(submission, action, modAction)
            else:
                data = {'embeds': self.__generateEmbed(submission, action, modAction)}
            self.log.debug(data)
            requests.post(self.webhook, json=data)

    def __setUsernote(self, action, submission, modAction):
        subredditUsernotes = Usernotes(reddit=self.reddit, subreddit=submission.subreddit)
        subredditUsernotes.addUsernote(user=submission.author, note=action.usernote_note, thing=submission, warningType=action.usernote_warning_type, mod=modAction.mod)

    def __substituteToolboxTokens(self, text, submission, header, footer):
        if text:
            if header:
                text = f'{header}\n\n---\n\n{text}'
            if footer:
                text = f'{text}\n\n---\n\n{footer}'
            return text.format(author=getattr(submission.author, 'name', '[deleted]'), subreddit=submission.subreddit, kind=thingTypes[submission.fullname[:2]],
                domain=submission.domain, title=submission.title, url=submission.shortlink)
        else:
            return None

    def __generateEmbed(self, submission: praw.models.reddit.submission.Submission, params, modAction: praw.models.ModAction):
        embed = embeds.Embed(title='Bot Removal Notification', url=submission.shortlink, description=params.description)
        if not submission.is_self:
            embed.set_image(url=submission.url)
        embed.add_field(name='Submission:', value=f'[{submission.title}]({submission.shortlink})', inline=False)
        if submission.author:
            embed.add_field(name='Author:', value=f'[{submission.author.name}](https://reddit.com/user/{submission.author.name})')
        else:
            embed.add_field(name='Author:', value='[deleted]')
        embed.add_field(name='Posted At:', value=time.strftime('%b %d, %Y %I:%M %p %Z', time.gmtime(submission.created_utc)))
        embed.add_field(name='Score:', value=f'{submission.score:,}')
        embed.add_field(name='Comments:', value=f'{submission.num_comments:,}')
        embed.add_field(name='Removed By:', value=f'{modAction._mod}')
        if params.ban:
            if params.ban_duration:
                if params.ban_duration > 1:
                    embed.add_field(name='Ban Duration:', value=f'{params.ban_duration:,} days')
                else:
                    embed.add_field(name='Ban Duration:', value=f'{params.ban_duration:,} day')
            else:
                embed.add_field(name='Ban Duration:', value='Permanent')
        modReports = self.__parseModReports(submission)
        if modReports:
            if not modReports[0][1] == 0:
                embed.add_field(name=f'Mod Reports ({modReports[0][1]:,}):', value=modReports[0][0])
            if not modReports[1][1] == 0:
                embed.add_field(name=f'Mod Reports Dismissed ({modReports[1][1]:,}):', value=modReports[1][0])
        userReports = self.__parseUserReports(submission)
        if userReports:
            if not userReports[0][1] == 0:
                embed.add_field(name=f'User Reports ({userReports[0][1]:,}):', value=userReports[0][0])
            if not userReports[1][1] == 0:
                embed.add_field(name=f'User Reports Dismissed ({userReports[1][1]:,}):', value=userReports[1][0])
        usernotesString = None
        if submission.author:
            usernotesString = self.__parseUsernotes(Usernotes(reddit=self.reddit, subreddit=submission.subreddit), submission.author.name)
        if usernotesString:
            embed.add_field(name='Usernotes:', value=usernotesString, inline=False)
        embed.set_footer(text=time.strftime('%B %d, %Y at %I:%M:%S %p %Z', time.gmtime()))
        return [embed.to_dict()]

    def __slackEmbedField(self, name, value, inline=True):
        return {"title": name, "value": value, "short": inline}

    def __generateSlackEmbed(self, submission: praw.models.reddit.submission.Submission, params, modAction: praw.models.ModAction):

        attachment = {
            "mrkdwn_in": ["text", "fields", "value"],
            "color": "#36a64f",
            "title": "Bot Removal Notification",
            "title_link": submission.shortlink,
            "text": params.description,
            "fields": [],
            "ts": time.gmtime()
        }
        if not submission.is_self:
            attachment['thumb_url'] = submission.url
        attachment['fields'].append(self.__slackEmbedField(name='Submission:', value=f'<{submission.shortlink}|{submission.title}>', inline=False))
        if submission.author:
            attachment['author_name'] = submission.author.name
            attachment['author_link'] = f'https://reddit.com/user/{submission.author.name}'
            attachment['author_icon'] = submission.author.icon_img
        else:
            attachment['author_name'] = '[deleted]'
        attachment['fields'].append(self.__slackEmbedField(name='Posted At:', value=time.strftime('%b %d, %Y %I:%M %p %Z', time.gmtime(submission.created_utc))))
        attachment['fields'].append(self.__slackEmbedField(name='Score:', value=f'{submission.score:,}'))
        attachment['fields'].append(self.__slackEmbedField(name='Comments:', value=f'{submission.num_comments:,}'))
        attachment['fields'].append(self.__slackEmbedField(name='Removed By:', value=f'{modAction._mod}'))
        if params.ban:
            if params.ban_duration:
                if params.ban_duration > 1:
                    attachment['fields'].append(self.__slackEmbedField(name='Ban Duration:', value=f'{params.ban_duration:,} days'))
                else:
                    attachment['fields'].append(self.__slackEmbedField(name='Ban Duration:', value=f'{params.ban_duration:,} day'))
            else:
                attachment['fields'].append(self.__slackEmbedField(name='Ban Duration:', value='Permanent'))
        modReports = self.__parseModReports(submission)
        if modReports:
            if not modReports[0][1] == 0:
                attachment['fields'].append(self.__slackEmbedField(name=f'Mod Reports ({modReports[0][1]:,}):', value=modReports[0][0]))
            if not modReports[1][1] == 0:
                attachment['fields'].append(self.__slackEmbedField(name=f'Mod Reports Dismissed ({modReports[1][1]:,}):', value=modReports[1][0]))
        userReports = self.__parseUserReports(submission)
        if userReports:
            if not userReports[0][1] == 0:
                attachment['fields'].append(self.__slackEmbedField(name=f'User Reports ({userReports[0][1]:,}):', value=userReports[0][0]))
            if not userReports[1][1] == 0:
                attachment['fields'].append(self.__slackEmbedField(name=f'User Reports Dismissed ({userReports[1][1]:,}):', value=userReports[1][0]))
        usernotesString = None
        if submission.author:
            usernotesString = self.__parseUsernotes(Usernotes(reddit=self.reddit, subreddit=submission.subreddit), submission.author.name)
        if usernotesString:
            attachment['fields'].append(self.__slackEmbedField(name='Usernotes:', value=usernotesString, inline=False))
        return {"channel": self.slackChannel, "attachments": [attachment]}

    def __setBan(self, submission: praw.models.Submission, params):
        self.subreddit.banned.add(submission.author, duration=params.ban_duration, ban_reason=params.ban_reason,
            ban_message=self.__substituteToolboxTokens(params.ban_message, submission, self.header, self.footer),
            note=self.__substituteToolboxTokens(params.ban_note, submission, self.header, self.footer))

    def __parseUserReports(self, submission: praw.models.reddit.submission.Submission):
        userReportsDismissed = []
        userReports = submission.user_reports
        if 'user_reports_dismissed' in vars(submission):
            for dismissedReport in submission.user_reports_dismissed:
                userReportsDismissed.append(dismissedReport)
        reportString = '{0[1]}: {0[0]}\n'
        final = ''
        for report in userReports:
            final += reportString.format(report)
        dismissedFinal = ''
        for report in userReportsDismissed:
            dismissedFinal += reportString.format(report)
        if len(final) == 0 and len(dismissedFinal) == 0:
            return
        else:
            return (final, len(userReports)), (dismissedFinal, len(userReportsDismissed))

    def __parseModReports(self, submission: praw.models.reddit.submission.Submission):
        modReportsDismissed = []
        modReports = submission.mod_reports
        if 'mod_reports_dismissed' in vars(submission):
            for dismissedReport in submission.mod_reports_dismissed:
                modReportsDismissed.append(dismissedReport)
        reportString = '{0[1]}: {0[0]}\n'
        final = ''
        for report in modReports:
            final += reportString.format(report)
        dismissedFinal = ''
        for report in modReportsDismissed:
            dismissedFinal += reportString.format(report)
        if len(final) == 0 and len(dismissedFinal) == 0:
            return
        else:
            return (final, len(modReports)), (dismissedFinal, len(modReportsDismissed))

    def __parseUsernotes(self, subredditUsernotes, user):
        usernoteStringLink = '[{}] [{}]({}) - by /u/{} - {}\n'
        usernoteString = '[{}] {} - by /u/{} - {}\n'
        final = ''
        notes = subredditUsernotes.getUsernotes(user)
        colors = subredditUsernotes.getUsernoteWarningColor()
        if user in notes and 'ns' in notes[user]:
            for note in notes[user]['ns']:
                w = colors[note['w']][0]
                n = note['n']
                l = note['l']
                m = note['m']
                t = timeago.format(datetime.datetime(*time.localtime(note['t'])[:6]))
                if len(l) == 0:
                    final += usernoteString.format(w, n, m, t)
                elif len(l) == 8:
                    if l[0] == 'l':
                        lstr = l.split(',')
                        submission = self.reddit.submission(lstr[1])
                        link = submission.shortlink
                        final += usernoteStringLink.format(w, n, link, m, t)
                    elif l[0] == 'm':
                        link = f'https://www.reddit.com/message/messages/{l.split(",")[1]}'
                        final += usernoteStringLink.format(w, n, link, m, t)
                if len(l) == 15 and l[0] == 'l':
                    comment = self.reddit.comment(lstr[2])
                    commentid = comment.id
                    submission = comment.submission
                    link = f'https://www.reddit.com{submission.permalink}{commentid}'
                    final += usernoteStringLink.format(w, n, link, m, t)
        else:
            return
        if len(final) == 0:
            return
        else:
            return final

def listWithCommas(items):
    if len(items) == 0:
        return ''
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f'{items[0]} and {items[1]}'
    return ', '.join(items[:-1]) + ', and ' + items[-1]

def flairBot(reddit, subreddit, webhook, webhook_type, header, footer, dsn):
    services = BotServices('FlairBot')
    reddit = praw.Reddit(**reddit)
    engine = create_engine(dsn)
    session = sessionmaker(bind=engine)()
    log = services.logger()
    subreddit = reddit.subreddit(subreddit)
    slack = webhook_type == 'slack'
    flairRemoval = FlairRemoval(reddit, subreddit, webhook, log, webhookEnabled=bool(webhook), slack=slack, header=header, footer=footer, session=session)
    checkModAction = flairRemoval.checkModAction
    log.info(f'{subreddit.display_name} | Starting FlairBot')
    while True:
        try:
            log.info(f'{subreddit.display_name} | Checking last 25 flair edits...')
            for modAction in subreddit.mod.log(action='editflair', limit=5):
                try:
                    checkModAction(modAction)
                except Exception as error:
                    log.exception(error)
                    pass
            log.info(f'{subreddit.display_name} | Scanning Mod Log')
            for modAction in flairRemoval.logStream():
                checkModAction(modAction)
        except KeyboardInterrupt:
            pass
        except Exception as error:
            log.exception(error)

class DaemonLogger:

    # noinspection PyDunderSlots,PyUnresolvedReferences
    def __init__(self, logger: logging.Logger, name, subreddit=True):
        self.log = logger
        self.name = ('', 'r/')[subreddit] + name

    def critical(self, message):
        self.log.critical(f'{self.name} | {message}')

    def error(self, message):
        self.log.error(f'{self.name} | {message}')

    def exception(self, message):
        self.log.exception(f'{self.name} | {message}')

    def warning(self, message):
        self.log.warning(f'{self.name} | {message}')

    def info(self, message):
        self.log.info(f'{self.name} | {message}')

    def debug(self, message):
        self.log.debug(f'{self.name} | {message}')

def sortList(items):
    items.sort()
    return items

def getChanges(results, previousResults):
    if previousResults != results:
        subNames = set(sortList([result.subreddit for result in results if result.enabled]))
        previousSubNames = set(sortList([result.subreddit for result in previousResults if result.enabled]))
        added = list(subNames.difference(previousSubNames))
        deleted = list(previousSubNames.difference(subNames))
        previousEnabled = sortList([r.subreddit for r in previousResults if r.enabled])
        previousDisabled = sortList([r.subreddit for r in previousResults if not r.enabled])
        gotEnabled = [r.subreddit for r in results if r.subreddit in previousDisabled and r.enabled]
        gotDisabled = [r.subreddit for r in results if r.subreddit in previousEnabled and not r.enabled]
        changed = [r for r in results if not r.subreddit in added + deleted + gotEnabled + gotDisabled and not r in previousResults]
        needStarted = [r for r in results if r.subreddit in added + gotEnabled] + [r for r in results if r in changed]
        needStopped = deleted + gotDisabled + [r.subreddit for r in results if r in changed]
        statuses = {}
        for i in added:
            statuses[i] = 'added'
        for i in deleted:
            statuses[i] = 'deleted'
        for i in gotEnabled:
            statuses[i] = 'enabled'
        for i in gotDisabled:
            statuses[i] = 'disabled'
        for i in changed:
            statuses[i.subreddit] = 'changed'
    else:
        needStarted, needStopped, statuses = [], [], {}
    return needStarted, needStopped, statuses

if __name__ == '__main__':
    # import pydevd_pycharm
    # pydevd_pycharm.settrace('24.225.29.166', port=2999, stdoutToServer=True, stderrToServer=True)
    services = BotServices('FlairBot')
    settings = getBotSettings('FlairBot', 'postgres')
    if sys.platform == 'darwin':
        settings['dbHost'] = settings['sshHost']
    url = f"postgresql://{settings['dbUser']}:{settings['dbPass']}@{settings['dbHost']}:5432/{settings['dbName']}"
    engine = create_engine(url)
    session = sessionmaker(bind=engine)()
    sessionManager = SessionManager(session)
    log = DaemonLogger(services.logger(), 'FlairBot Daemon', False)
    previousResults = results = session.query(Subreddit).all()
    results = [i for i in results if i.enabled]
    subreddits = {result.subreddit: {
        'reddit': services.reddit(result.bot_account).config._settings,
        'webhook': result.webhook,
        'webhook_type': result.webhook_type,
        'header': result.header,
        'footer': result.footer
    } for result in results}
    flairBots = {subreddit: Process(target=flairBot, kwargs={'subreddit': subreddit, **subreddits[subreddit], 'dsn': url}) for subreddit in subreddits}
    for subreddit in subreddits:
        bot = flairBots[subreddit]
        bot.start()

    while True:
        results = session.query(Subreddit).all()
        needStarted, needStopped, statuses = getChanges(results, previousResults)
        previousResults = results
        if needStarted or needStopped:
            log.info('Change detected')
            for result in needStopped:
                log.info(f'FlairBot for r/{result} was {statuses[result]}...stopping')
                if result in subreddits and result in flairBots:
                    try:
                        flairBots[result].terminate()
                        subreddits.pop(result)
                        log.info(f'r/{result} stopped')
                    except Exception as error:
                        log.error(f'Error stopping r/{result}')
                        log.exception(error)
            for result in needStarted:
                log.info(f'FlairBot for r/{result.subreddit} was {statuses[result.subreddit]}...starting')
                if result.subreddit in flairBots:
                    flairBots[result.subreddit].terminate()
                subreddits[result.subreddit] = {
                    'reddit': services.reddit(result.bot_account).config._settings,
                    'webhook': result.webhook,
                    'webhook_type': result.webhook_type,
                    'header': result.header,
                    'footer': result.footer
                }
                flairBots[result.subreddit] = bot = Process(target=flairBot, kwargs={'subreddit': result.subreddit, **subreddits[result.subreddit]})
                bot.start()
        subreddits = {result.subreddit: {
            'reddit': services.reddit(result.bot_account).config._settings,
            'webhook': result.webhook,
            'webhook_type': result.webhook_type,
            'header': result.header,
            'footer': result.footer
        } for result in results}
        log.debug('sleeping for 5 seconds')
        time.sleep(5)