from BotUtils.CommonUtils import BotServices

services = BotServices('FlairBot')

sql = services.postgres()
subreddit = 'BikiniBottomTwitter'
botName = 'Sponge-Tron'
webhook = 'https://discordapp.com/api/webhooks/536995656267726854/Fg-HgyOAW3Po1emRqFTeXwvc0zz5R3PhhlHwZY_DbXGJ5cRUOoWBgINzH5H3b0RXoLw7'
header = '''Hi {author}, thanks for submitting to /r/{subreddit.display_name}!\n\n\nHowever, your submission has been removed. This action was taken because:'''
footer = 'If you disagree with this action, you can [message the mods](https://www.reddit.com/message/compose?to=%2Fr%2F{subreddit.display_name}). Please include a link to your post so that we can see it.'
data = (
    subreddit,
    botName,
    webhook,
    'discord',
    header,
    footer
)
sql.execute('INSERT INTO flairbots.subreddits (subreddit, bot_account, webhook, webhook_type, header, footer) VALUES (%s, %s, %s, %s, %s, %s)', data)

removalReasons = {
    'removed - repost': {
        'description': 'Repost',
        'commentReply': f'It\'s a repost'
    },
    'removed - no titles as meme captions': {
        'description': 'Title as meme caption',
        'commentReply': f'We do not allow titles as meme captions. Feel free to caption it and post again.'
    },
    'removed - low effort': {
        'description': 'Low effort',
        'commentReply': f'It\'s really low effort content.'
    },
    'flairtext': {
        'description': 'This the description that gets sent to the log channel',
        'commentReply': 'blah blah blah\n\nsupports multiple lines',
        'lock': True,
        'ban': {
            'duration': 1,
            'ban_reason': 'Ban reason (str)',
            'ban_message': 'Sent to user (str)',
            'ban_note': 'Private Mod note (str)'
        },
        'usernote': {
            'usernote': 'Note',
            'usernoteWarningType': 'spamwatch'
        }
    },
}

for flair, config in removalReasons.items():
    data = (
        subreddit,
        flair,
        config.get('description', None),
        config.get('commentReply', None),
        config.get('lock', False),
        config.get('lockComment', False),
        config.get('ban', None) is not None,
        config.get('ban', {}).get('duration', None),
        config.get('ban', {}).get('ban_reason', None),
        config.get('ban', {}).get('ban_message', None),
        config.get('ban', {}).get('ban_note', None),
        config.get('usernote', None) is not None,
        config.get('usernote', {}).get('usernote', None),
        config.get('usernote', {}).get('usernoteWarningType', None),
    )
    sql.execute('INSERT INTO flairbots.removal_reasons (subreddit, flair_text, description, comment, lock, lock_comment, ban, ban_duration, ban_reason, ban_message, ban_note, usernote, usernote_note, usernote_warning_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', data)