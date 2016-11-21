# import vlc
#
# finish = 0
#
#
# def SongFinished(event):
#     global finish
#     print "Event reports - finished"
#     finish = 1
#
#
# instance = vlc.Instance()
# player = instance.media_player_new()
# media = instance.media_new_path('music/krtheme.wav')  # Your audio file here
# player.set_media(media)
# events = player.event_manager()
# events.event_attach(vlc.EventType.MediaPlayerEndReached, SongFinished)
# player.play()
# while finish == 0:
#     sec = player.get_time() / 1000
#     m, s = divmod(sec, 60)
#     print "%02d:%02d" % (m, s)


