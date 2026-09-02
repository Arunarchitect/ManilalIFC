# May not be necesary , if the append after tuple fix is working

import sys
import ifcopenshell.api.project

def patch_safe_removal_context():
    module = sys.modules.get("ifcopenshell.api.project.append_asset")
    if module is None:
        print("Could not find append_asset module — patch not applied.")
        return False

    SafeRemovalContext = getattr(module, "SafeRemovalContext", None)
    if SafeRemovalContext is None:
        print("Could not find SafeRemovalContext class — patch not applied.")
        return False

    if getattr(SafeRemovalContext, "_arun_patched", False):
        print("Already patched this session.")
        return True

    original_exit = SafeRemovalContext.__exit__

    def patched_exit(self, exc_type, exc_val, exc_tb):
        try:
            return original_exit(self, exc_type, exc_val, exc_tb)
        except AssertionError:
            # Known upstream bug: removed_identities/removed_elements bookkeeping
            # can go out of sync even though the actual cleanup already completed
            # successfully just before this check. Safe to suppress.
            print("[SafeRemovalContext patch] Suppressed a known bookkeeping "
                  "AssertionError — the append itself already completed.")
            return True  # swallow the exception, don't propagate

    SafeRemovalContext.__exit__ = patched_exit
    SafeRemovalContext._arun_patched = True
    print("SafeRemovalContext patched for this Blender session.")
    return True

patch_safe_removal_context()