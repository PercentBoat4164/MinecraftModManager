import MultiMC

# Check if compatible with current instance
if __name__ == "__main__":
    multimc_manager = MultiMC.MultiMC()
    current_instance = multimc_manager.ask_for_instance()
    current_instance.get_all_mods()
    current_instance.update_all_mods()
