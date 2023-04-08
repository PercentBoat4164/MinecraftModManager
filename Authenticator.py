import json.encoder
import os
import threading
import time
import minecraft_launcher_lib.utils
import webview


class Authenticator:
    CLIENT_ID = "nnnnnnnn-nnnn-nnnn-nnnn-nnnnnnnnnnnn"
    REDIRECT_URL = "https://example.com"
    USER_DATA_DIRECTORY = os.path.join(os.getcwd(), "Users")
    os.makedirs(USER_DATA_DIRECTORY, exist_ok=True)

    def __init__(self):
        pass

    @classmethod
    def _get_code_url(cls, login_url, window=None):
        def _wait():
            url = window.get_current_url()
            title = window.title
            window.load_url(login_url)
            window.set_title("Minecraft Login")
            while not minecraft_launcher_lib.microsoft_account.url_contains_auth_code(window.get_current_url()):
                time.sleep(.1)
            nonlocal code_url
            code_url = window.get_current_url()
            window.set_title(title)
            window.load_url(url)
            window.destroy()

        code_url = ""
        if not window:
            window = webview.create_window("Minecraft Login", login_url)
        threading.Thread(target=_wait).start()
        webview.start(private_mode=False)
        return code_url

    def get_login_data(self, window=None):
        login_url, state, code_verifier = minecraft_launcher_lib.microsoft_account.get_secure_login_data(self.CLIENT_ID,
                                                                                                         self.REDIRECT_URL)
        code_url = self._get_code_url(login_url, window)
        auth_code = minecraft_launcher_lib.microsoft_account.parse_auth_code_url(code_url, state)
        login_data = minecraft_launcher_lib.microsoft_account.complete_login(self.CLIENT_ID, None, self.REDIRECT_URL,
                                                                             auth_code, code_verifier)
        with open(os.path.join(self.USER_DATA_DIRECTORY, login_data.get("name") + ".json"), "w") as file:
            file.write(json.encoder.JSONEncoder().encode({"refresh_token": login_data.get("refresh_token")}))
        return login_data

    def refresh(self, username):
        with open(os.path.join(self.USER_DATA_DIRECTORY, username + ".json"), "r+") as file:
            user_data_on_disk = json.decoder.JSONDecoder().decode(file.read())
            user_data = minecraft_launcher_lib.microsoft_account.refresh_authorization_token(self.CLIENT_ID, None,
                                                                                             self.REDIRECT_URL,
                                                                                             user_data_on_disk.get(
                                                                                                 "refresh_token"))
            user_data_on_disk["refresh_token"] = user_data.get("refresh_token")
            file.write(json.encoder.JSONEncoder().encode(user_data_on_disk))
        return user_data


if __name__ == "__main__":
    print(Authenticator().get_login_data())
    print(Authenticator().refresh("PercentBoat4164"))
