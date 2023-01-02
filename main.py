import MultiMC
import modrinth
import time

# Check if compatible with current instance
if __name__ == "__main__":
    authedUser = modrinth.Users.AuthenticatedUser('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')

    multimc_manager = MultiMC.MultiMC()
    current_instance = multimc_manager.instances["1.19.2"]
    current_instance.infer_all_existing_mods()
    print("Waiting a minute to avoid the ratelimit.")
    time.sleep(60)
    current_instance.update_all_inferred_mods()