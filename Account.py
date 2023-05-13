import json
import os
import threading
import time

import requests
from PIL import Image

import minecraft_launcher_lib
import webview

import customtkinter


class AccountsListEntry(customtkinter.CTkFrame):
    def __init__(self, master, account, command=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.radio = customtkinter.CTkRadioButton(self, text=account.name, command=command)
        self.image = customtkinter.CTkLabel(self, text="",
                                            image=customtkinter.CTkImage(account.active_skin))

    def pack(self, **kwargs):
        super().pack(**kwargs)
        self.radio.grid(column=1, row=0, padx=4, pady=4)
        self.image.grid(column=0, row=0, padx=4, pady=4)


class Account:
    _CLIENT_ID = "nnnnnnnn-nnnn-nnnn-nnnn-nnnnnnnnnnnn"
    _REDIRECT_URL = "https://example.com"
    _USER_DATA_DIRECTORY = os.path.join(os.getcwd(), "Users")
    os.makedirs(_USER_DATA_DIRECTORY, exist_ok=True)

    def __init__(self, file=None):
        self.active_skin = None
        self.active_skin_path = None
        self.active_skin_id = None
        self.refresh_token = None
        with open("credentials.json", "r") as f:
            credentials = json.decoder.JSONDecoder().decode(f.read())
            self._CLIENT_ID = credentials["client_id"]
            self._REDIRECT_URL = credentials["redirect_url"]
        if file is None:
            login_data = self._get_login_data()
            if login_data is None:
                raise AssertionError("User did not finish login process.")
            self.name = login_data["name"]
            login_data_no_access_token = login_data
            login_data_no_access_token.pop("access_token")
            self._set_account_info(login_data_no_access_token)
            self._get_account_info()
        else:
            self._get_account_info(os.path.basename(file))

    def _get_account_info(self, name=None):
        def get_skin_icon():
            skin_icon = Image.open(self.active_skin_path)
            w, h = skin_icon.size
            w /= 8
            h /= 8
            skin_icon = skin_icon.crop((w, h, 2 * w, 2 * h))
            return skin_icon

        with open(os.path.join(self._USER_DATA_DIRECTORY, name if name is not None else self.name + ".json")) as f:
            account_info = json.JSONDecoder().decode(f.read())
        self.name = account_info["name"]
        self.refresh_token = account_info["refresh_token"]
        for skin in account_info["skins"]:
            if skin["state"] == "ACTIVE":
                self.active_skin_id = skin["id"]
                self.active_skin_path = os.path.join(self._USER_DATA_DIRECTORY, self.active_skin_id + '.png')
                if os.path.exists(self.active_skin_path):
                    self.active_skin = get_skin_icon()
                else:
                    pass
                    with open(self.active_skin_path, "wb") as f:
                        f.write(requests.get(skin["url"]).content)
                    self.active_skin = get_skin_icon()

    def _set_account_info(self, account_info):
        with open(os.path.join(self._USER_DATA_DIRECTORY, self.name + ".json"), "w") as f:
            f.write(json.JSONEncoder().encode(account_info))

    @classmethod
    def _show_login_window(cls, login_url):
        code_url = None
        window = webview.create_window("Minecraft Login", login_url)

        def _wait():
            while not minecraft_launcher_lib.microsoft_account.url_contains_auth_code(window.get_current_url()):
                time.sleep(.1)
            nonlocal code_url
            code_url = window.get_current_url()
            window.destroy()

        threading.Thread(target=_wait).start()
        webview.start(private_mode=True)
        return code_url

    def _get_login_data(self):
        login_url, state, code_verifier = minecraft_launcher_lib.microsoft_account.get_secure_login_data(
            self._CLIENT_ID,
            self._REDIRECT_URL)
        code_url = self._show_login_window(login_url)
        if code_url is None:
            return None
        auth_code = minecraft_launcher_lib.microsoft_account.parse_auth_code_url(code_url, state)
        login_data = minecraft_launcher_lib.microsoft_account.complete_login(self._CLIENT_ID, None, self._REDIRECT_URL,
                                                                             auth_code, code_verifier)
        with open(os.path.join(self._USER_DATA_DIRECTORY, login_data.get("name") + ".json"), "w") as file:
            file.write(json.encoder.JSONEncoder().encode({"refresh_token": login_data.get("refresh_token")}))
        return login_data

    def refresh(self, username):
        with open(os.path.join(self._USER_DATA_DIRECTORY, username + ".json"), "r+") as file:
            user_data_on_disk = json.decoder.JSONDecoder().decode(file.read())
            user_data = minecraft_launcher_lib.microsoft_account.refresh_authorization_token(self._CLIENT_ID, None,
                                                                                             self._REDIRECT_URL,
                                                                                             user_data_on_disk.get(
                                                                                                 "refresh_token"))
            user_data_on_disk["refresh_token"] = user_data.get("refresh_token")
            file.write(json.encoder.JSONEncoder().encode(user_data_on_disk))
        return user_data


def get_all_accounts():
    accounts = []
    for file in os.listdir(Account._USER_DATA_DIRECTORY):
        if file.endswith(".json"):
            accounts.append(Account(file))
    return accounts
