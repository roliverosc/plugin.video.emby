# -*- coding: utf-8 -*-

#################################################################################################

import logging

import xbmc

from helper import _, settings, dialog, JSONRPC, compare_version

#################################################################################################

LOG = logging.getLogger("EMBY."+__name__)

#################################################################################################


class Setup(object):

    def __init__(self):

        self.setup()
        self.set_web_server()

        LOG.info("---<[ setup ]")

    def set_web_server(self):

        ''' Enable the webserver if not enabled. This is used to cache artwork.
            Will only test once, if it fails, user will be notified only once.
        '''
        if settings('enableTextureCache.bool'):

            get_setting = JSONRPC('Settings.GetSettingValue')

            if not self.get_web_server():

                set_setting = JSONRPC('Settings.SetSetingValue')
                set_setting.execute({'setting': "services.webserverport", 'value': 8080})
                set_setting.execute({'setting': "services.webserver", 'value': True})

                if not self.get_web_server():

                    settings('enableTextureCache.bool', False)
                    dialog("ok", heading="{emby}", line1=_(33103))
                    
                    return

            result = get_setting.execute({'setting': "services.webserverport"})
            settings('webServerPort', str(result['result']['value'] or ""))
            result = get_setting.execute({'setting': "services.webserverusername"})
            settings('webServerUser', str(result['result']['value'] or ""))
            result = get_setting.execute({'setting': "services.webserverpassword"})
            settings('webServerPass', str(result['result']['value'] or ""))
            settings('useWebServer.bool', True)

    def get_web_server(self):

        result = JSONRPC('Settings.GetSettingValue').execute({'setting': "services.webserver"})

        try:
            return result['result']['value']
        except (KeyError, TypeError):
            return False

    def setup(self):

        minimum = "3.0.24"
        cached = settings('MinimumSetup')

        if cached == minimum:
            return

        if not cached:

            self._is_mode()
            LOG.info("Add-on playback: %s", settings('useDirectPaths') == "0")
            self._is_artwork_caching()
            LOG.info("Artwork caching: %s", settings('enableTextureCache.bool'))
            self._is_empty_shows()
            LOG.info("Sync empty shows: %s", settings('syncEmptyShows.bool'))
            self._is_rotten_tomatoes()
            LOG.info("Sync rotten tomatoes: %s", settings('syncRottenTomatoes.bool'))
            self._is_multiep()
            LOG.info("Enable multi episode label: %s", settings('displayMultiEpLabel.bool'))

        """
        if compare_version(cached or minimum, "3.0.24") <= 0:

            self._is_rotten_tomatoes()
            LOG.info("Sync rotten tomatoes: %s", settings('syncRottenTomatoes.bool'))
        """

        # Setup completed
        settings('MinimumSetup', minimum)

    def _is_mode(self):

        ''' Setup playback mode. If native mode selected, check network credentials.
        '''
        value = dialog("yesno",
                       heading=_('playback_mode'),
                       line1=_(33035),
                       nolabel=_('addon_mode'),
                       yeslabel=_('native_mode'))

        settings('useDirectPaths', value="1" if value else "0")

        if value:
            dialog("ok", heading="{emby}", line1=_(33145))

    def _is_artwork_caching(self):

        if settings('lowPowered.bool'):

            LOG.info("Artwork caching ignored due to platform limitation.")
            settings('enableTextureCache.bool', True)

            return

        value = dialog("yesno", heading="{emby}", line1=_(33117))
        settings('enableTextureCache.bool', value)

    def _is_empty_shows(self):

        value = dialog("yesno", heading="{emby}", line1=_(33100))
        settings('syncEmptyShows.bool', value)

    def _is_rotten_tomatoes(self):

        value = dialog("yesno", heading="{emby}", line1=_(33188))
        settings('syncRottenTomatoes.bool', value)

    def _is_music(self):

        value = dialog("yesno", heading="{emby}", line1=_(33039))
        settings('enableMusic.bool', value=value)

    def _is_multiep(self):

        value = dialog("yesno", heading="{emby}", line1=_(33213))
        settings('displayMultiEpLabel.bool', value=value)
