import enum
import utils


class Status(enum.Enum):
    registrationVerification = "10"
    keyEnter = "11"
    commandName = "12"
    captainName = "131"
    captainPhoneNumber = "132"
    teammateName = "14"


statusErrorMsg = {
    Status.keyEnter.value: "Не введено підходящих данних, будь ласка введіть ключ реєстрації",
    Status.commandName.value: "Не введено підходящих данних, будь ласка введіть назву команди",
    Status.captainName.value: "Не введено підходящих данних, будь ласка введіть Прізвище та Ім'я капітана",
    Status.captainPhoneNumber.value: "Не введено підходящих данних, будь ласка введіть номер телефону капітана",
    Status.teammateName.value: "Не введено підходящих данних, будь ласка введіть Прзівище та Ім'я члена команди",
    Status.registrationVerification.value: "Вибачте я вас не розумію, будь ласка виберіть правильну відповідь"
}

stagesMap = {
    Status.keyEnter.value: utils.Registration.registration_enterKey,
    Status.commandName.value: utils.Registration.registration_commandName,
    Status.captainName.value: utils.Registration.registration_captainName,
    Status.captainPhoneNumber.value: utils.Registration.registration_captainPhoneNumber,
    Status.teammateName.value: utils.Registration.registration_teammateName,
    Status.registrationVerification.value: utils.Registration.registration_registrationVerification
}