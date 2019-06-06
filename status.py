import enum
import utils


class Status(enum.Enum):
    keyEnter = "11"
    commandName = "12"
    captainName = "131"
    captainPhoneNumber = "132"
    teammateName = "14"


statusErrorMsg = {
    Status.keyEnter: "Не введено підходящих данних, будь ласка введіть ключ реєстрації",
    Status.commandName: "Не введено підходящих данних, будь ласка введіть назву команди",
    Status.captainName: "Не введено підходящих данних, будь ласка введіть Прізвище та Ім'я капітана",
    Status.captainPhoneNumber: "Не введено підходящих данних, будь ласка введіть номер телефону капітана",
    Status.teammateName: "Не введено підходящих данних, будь ласка введіть Прзівище та Ім'я члена команди"
}

stagesMap = {
    Status.keyEnter.value: utils.registration_enterKey,
    Status.commandName.value: utils.registration_commandName,
    Status.captainName.value: utils.registration_captainName,
    Status.captainPhoneNumber.value: utils.registration_captainPhoneNumber,
    # Status.teammateName.value: utils.registration_teammateName
}