import MultiMC

# Check if compatible with current instance
if __name__ == "__main__":
    multimc_manager = MultiMC.MultiMC()
    current_instance = multimc_manager.instances["1.19.3"]
    current_instance.get_all_mods()
    current_instance.update_all_mods()
