pyDiscuzRobot
=============

A Robot which realize Discuz API (unofficial).

## Usage

    from DiscuzRobot import DiscuzRobot as DR
    
    # Initial
    r = DR('http://demo.discuz.com/', 'username', 'password')

    # Login
    r.login()

    # Publish, first arg is 'fid'
    r.publish(2, u'Subject', u'Message')

    # Reply, first arg is 'tid'
    r.reply(1, u'Subject', u'Message')
