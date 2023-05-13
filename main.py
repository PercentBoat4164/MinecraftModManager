import multiprocessing
import tkinter
import customtkinter

import Account


class SettingsView(customtkinter.CTkScrollableFrame):
    def __init__(self, master, layout: list, command=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self._layout = layout
        self._command = command

        def build_ui(elements, current_master):
            old_master = current_master
            sub_elements = []
            sub_elements_dict = {}
            grid_row = 0
            heading = ""

            for element in elements:
                if type(element) is list:
                    new_elements, new_elements_dict = build_ui(element, current_master)
                    sub_elements.append(new_elements)
                    sub_elements_dict.update(new_elements_dict)
                elif type(element) is str:
                    heading = element
                    current_master = customtkinter.CTkFrame(old_master)
                    sub_elements.append((current_master, 0, grid_row, 1))
                    grid_row += 1
                    sub_elements.append((customtkinter.CTkLabel(current_master, text=element), 0, grid_row, 2))
                    grid_row += 1
                elif type(element) is dict:
                    if "Options" in element.keys():
                        sub_elements.append(
                            (customtkinter.CTkLabel(current_master, text=element["Name"]), 0, grid_row, 1))
                        sub_elements.append((customtkinter.CTkOptionMenu(current_master, values=element["Options"],
                                                                         command=lambda *args: self._command(self)), 1,
                                             grid_row, 1))
                        sub_elements_dict.update({element["Name"]: sub_elements[-1][0]})
                    grid_row += 1
            return sub_elements, {heading: sub_elements_dict}

        self._ui_elements, self._ui_elements_dict = build_ui([self._layout], self)
        self._ui_elements_dict = self._ui_elements_dict[""]

    def __getitem__(self, key: str):
        return self._ui_elements_dict[key]

    def _place_elements(self, elements):
        for element in elements:
            if type(element) is list:
                self._place_elements(element)
            else:
                element[0].grid(column=element[1], row=element[2], columnspan=element[3], padx=4, pady=4)

    def pack(self, **kwargs):
        super().pack(**kwargs)

        self._place_elements(self._ui_elements)

    def grid(self, **kwargs):
        super().grid(**kwargs)

        self._place_elements(self._ui_elements)


class ListView(customtkinter.CTkScrollableFrame):
    def __init__(self, master, element_type, elements=(), *args, **kwargs):
        super().__init__(master)
        self._element_type = element_type
        self._elements = []
        for element in elements:
            self.add(len(self) - 1, *element)

    def add(self, index, *args, **kwargs):
        element = self._element_type(self, *args, **kwargs)
        element.pack()
        self._elements.insert(index, element)

    def remove(self, index):
        self._elements[index].destroy()
        self.remove(index)

    def __getitem__(self, index):
        return self._elements[index]

    def __setitem__(self, key, *args):
        self._elements[key] = self._element_type(*args)

    def __len__(self):
        return len(self._elements)

    def __iter__(self):
        return self._elements


class TabView(customtkinter.CTkTabview):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.tabs = {}

    def add(self, name):
        tab = super().add(name)
        self.tabs.__setitem__(name, tab)
        return tab

    def __getitem__(self, key):
        return self.tabs.__getitem__(key)


class MinecraftModManager(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        customtkinter.set_default_color_theme("green")

        # Build UI
        self.tab_view = TabView(self)
        self.tab_view.add("Settings")
        settings_layout = [
            "Appearance",
            {"Name": "Mode",
             "Options": ["System", "Light", "Dark"],
             "Description": "PLACEHOLDER DESCRIPTION"}
        ]
        self.settings = SettingsView(self.tab_view["Settings"], settings_layout,
                                     command=lambda settings_view: customtkinter.set_appearance_mode(
                                         settings_view["Appearance"]["Mode"].get()))
        self.settings.pack(pady=4)

        self.tab_view.add("Accounts")
        self.list_view = ListView(self.tab_view["Accounts"], Account.AccountsListEntry, [[account] for account in Account.get_all_accounts()])
        new_account_button = customtkinter.CTkButton(self.tab_view["Accounts"], text="Add New Account",
                                                     command=self.add_new_account)

        self.list_view.pack(pady=4)
        new_account_button.pack(pady=4)

        # Update UI
        self.update_ui()

    def add_new_account(self):
        try:
            new_account = Account.Account()
        except AssertionError:
            pass
        else:
            self.list_view.add(0, new_account)

    def update_ui(self, event=None):
        self.tab_view.pack()
        self.settings.pack()


def update_ui(event):
    print("update")


def change_theme(choice):
    customtkinter.set_default_color_theme(choice)


if __name__ == "__main__":
    multiprocessing.freeze_support()

    app = MinecraftModManager()
    app.mainloop()
