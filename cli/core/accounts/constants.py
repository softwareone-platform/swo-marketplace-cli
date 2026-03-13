from types import MappingProxyType

CREATING = "creating"
FETCHING = "fetching"
READING = "reading"
REMOVING = "removing"

STATUS_MSG = MappingProxyType({
    CREATING: "Making account",
    FETCHING: "Fetching account information",
    READING: "Reading accounts from the configuration file",
    REMOVING: "Removing account",
})
