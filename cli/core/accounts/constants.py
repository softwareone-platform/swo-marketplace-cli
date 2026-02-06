from typing import Final

CREATING: Final = "creating"
FETCHING: Final = "fetching"
READING: Final = "reading"
REMOVING: Final = "removing"

STATUS_MSG: Final = {
    CREATING: "Making account",
    FETCHING: "Fetching account information",
    READING: "Reading accounts from the configuration file",
    REMOVING: "Removing account",
}
