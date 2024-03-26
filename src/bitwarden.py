# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet
import json
import traceback
import urllib.error
import urllib.parse

class bitwarden(kp.Plugin):
    API_URL = "http://localhost:8087"

    ACTION_COPY_USER = "copy_user"
    ACTION_COPY_PASSWORD = "copy_password"
    ACTION_COPY_TOPT = "copy_topt"
    ACTION_OPEN_URL = "open_url"

    ITEMCAT_RESULT = kp.ItemCategory.USER_BASE + 2
    CREDENTIAL_RETRIVAL = "dynamic"

    """
    One-line description of your plugin.

    This block is a longer and more detailed description of your plugin that may
    span on several lines, albeit not being required by the application.

    You may have several plugins defined in this module. It can be useful to
    logically separate the features of your package. All your plugin classes
    will be instantiated by Keypirinha as long as they are derived directly or
    indirectly from :py:class:`keypirinha.Plugin` (aliased ``kp.Plugin`` here).

    In case you want to have a base class for your plugins, you must prefix its
    name with an underscore (``_``) to indicate Keypirinha it is not meant to be
    instantiated directly.

    In rare cases, you may need an even more powerful way of telling Keypirinha
    what classes to instantiate: the ``__keypirinha_plugins__`` global variable
    may be declared in this module. It can be either an iterable of class
    objects derived from :py:class:`keypirinha.Plugin`; or, even more dynamic,
    it can be a callable that returns an iterable of class objects. Check out
    the ``StressTest`` example from the SDK for an example.

    Up to 100 plugins are supported per module.

    More detailed documentation at: http://keypirinha.com/api/plugin.html
    """
    def __init__(self):
        super().__init__()

    def on_start(self):
        # TODO maybe start api server
        # kpu.shell_execute("bw serve", verb='open', detect_nongui=True, api_flags=None, terminal_cmd=None, show=-1)
        # get config 
        settings = self.load_settings()
        self.CREDENTIAL_RETRIVAL = settings.get_stripped(
            "credential_retrival",
            section="bitwarden",
            fallback="static")
        self.API_URL = settings.get_stripped(
            "bitwarden_api",
            section="bitwarden",
            fallback="http://localhost:8087")
        #register actions
        actions = [
            self.create_action(
                name=self.ACTION_COPY_USER,
                label="Copy Username",
                short_desc="Copy username to clipboard"),
            self.create_action(
                name=self.ACTION_COPY_PASSWORD,
                label="Copy Password",
                short_desc="Copy password to clipboard"),
            self.create_action(
                name=self.ACTION_COPY_TOPT,
                label="Copy One Time Token",
                short_desc="Copy One Time Token to clipboard"),
            self.create_action(
                name=self.ACTION_OPEN_URL,
                label="Open URL",
                short_desc="Open the URL in clipboard")]
        self.set_actions(self.ITEMCAT_RESULT, actions)

    def on_catalog(self):
        # if the catalgo should be prefilled
        if self.CREDENTIAL_RETRIVAL == "static":
            print("build catalog")
            # call api. 
            if kp.should_terminate():
                return
            #fill catalog
            catalog = []
            try: 
                opener = kpnet.build_urllib_opener()
                with opener.open(self.API_URL+"/list/object/items", timeout=30,) as conn:
                    response = conn.read()
                #get objects.
                results = self._parse_api_response(response)

                for result in results: 
                    #print(result)
                    login = result.get("login", {})
                    if (result["type"] == 1): #website credentials
                        catalog.append(self.create_item(
                            category=self.ITEMCAT_RESULT,
                            label=result["name"],
                            short_desc=str(login.get("username", "-")),
                            target=str(login.get("password","") ),
                            args_hint=kp.ItemArgsHint.ACCEPTED,
                            hit_hint=kp.ItemHitHint.NOARGS,
                        	data_bag=json.dumps(result)))
                    # TODO implement other item types
                    elif (result["type"] == 2): #secure note
                        continue
                    elif (result["type"] == 3): #card
                        continue
                    elif (result["type"] == 4): #identity
                        continue
            except urllib.error.HTTPError as exc:
                catalog.append(self.create_error_item(
                    label="bitwarden", short_desc=str(exc)))
            except Exception as exc:
                catalog.append(self.create_error_item(
                    label="bitwarden", short_desc="Error: " + str(exc)))
                traceback.print_exc()
            self.set_catalog(catalog)
            print(f"catalog finished: {str(len(catalog))} items added")
        # if items are fetched dynamically do nothing
        else:
            print("dynamic credential retrieval")

    def on_suggest(self, user_input, items_chain):
        # if items are fetched dynamically
        if self.CREDENTIAL_RETRIVAL == "dynamic":
            #start at a length of 3
            if len(user_input) < 3:
                return
            suggestions = []
            results = []
            try:
                # get possible items
                opener = kpnet.build_urllib_opener()
                url = self.API_URL+"/list/object/items?search="+user_input
                with opener.open(url) as conn:
                    response = conn.read()

                # get objects
                results = self._parse_api_response(response)
            except urllib.error.HTTPError as exc:
                suggestions.append(self.create_error_item(
                    label=user_input, short_desc=str(exc)))
            except Exception as exc:
                suggestions.append(self.create_error_item(
                    label=user_input, short_desc="Error: " + str(exc)))
                traceback.print_exc()

            # create a suggestion from api's response, if any
            for result in results:
                login = result.get("login", {})
                suggestions.append(self.create_item(
                    category=self.ITEMCAT_RESULT,
                    label=result["name"],
                    short_desc=str(login.get("username", "-")),
                    target=str(login.get("password","") ),
                    args_hint=kp.ItemArgsHint.ACCEPTED,
                    hit_hint=kp.ItemHitHint.NOARGS,
                    data_bag=json.dumps(result))
                )

            # push suggestions if any
            if suggestions:
                self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.NONE)

    def on_execute(self, item, action):
        # default: copy password. other actions: copy username or TOPT, open URL in browser
        if action and action.name() in (self.ACTION_COPY_USER,
                                        self.ACTION_COPY_TOPT,
                                        self.ACTION_OPEN_URL):
            result = json.loads(item.data_bag())
            print(result)
            login = result.get("login", {})
            if action.name() == self.ACTION_OPEN_URL:
                uris = login.get("uris",[])
                url_entry = uris[0]
                uri = url_entry.get("uri", "")
                kpu.shell_execute(uri, verb='open', detect_nongui=True, api_flags=None, terminal_cmd=None, show=-1)
            elif action.name() == self.ACTION_COPY_USER:
                kpu.set_clipboard(login.get("username", ""))
            elif action.name() == self.ACTION_COPY_TOPT:
                #retrieve TOPT from API
                opener = kpnet.build_urllib_opener()
                url = self.API_URL+"/object/totp/"+result.get("id", "")
                with opener.open(url) as conn:
                    response = conn.read()

                # parse response from the api
                results = self._parse_api_response(response)
                print(results)
                kpu.set_clipboard(results)
        # default action: copy result (ACTION_COPY_RESULT)
        else:
            kpu.set_clipboard(item.target())

    def _parse_api_response(self, response):
        try:
            json_object = json.loads(response)
            json_data_list = json_object["data"]["data"]
        except: 
            return json.loads("{'name':'error'}")
        return json_data_list
