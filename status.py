import enum
import utils


class Status(enum.Enum):
    registration_keyEnter = "11"
    registration_commandName = "12"
    registration_captainName = "131"
    registration_captainPhoneNumber = "132"
    registration_teammateName = "14"
    registration_Verification = "10"
    quest_keyEnter = "21"


statusErrorMsg = {
    Status.registration_keyEnter.value: "Вибачте, але ключ не розпізнано. Спробуйте ще раз.\nЯкщо ключ не розпізнається з фотографії, спробуйте просканувати його в сторонньому додатку та надішліть мені отриманий текст.",
    Status.registration_commandName.value: "Не введено підходящих даних, будь ласка введіть назву команди.",
    Status.registration_captainName.value: "Не введено підходящих даних, будь ласка введіть Прізвище та Ім'я капітана.",
    Status.registration_captainPhoneNumber.value: "Не введено підходящих даних, будь ласка введіть номер телефону капітана.",
    Status.registration_teammateName.value: "Не введено підходящих даних, будь ласка введіть Прзівище та Ім'я члена команди.",
    Status.registration_Verification.value: "Вибачте я вас не розумію, будь ласка виберіть правильну відповідь.",
    Status.quest_keyEnter.value: "Вибачте, але ключ не розпізнано. Спробуйте ще раз.\nЯкщо ключ не розпізнається з фотографії, спробуйте просканувати його в сторонньому додатку та надішліть мені отриманий текст."

}

stagesMap = {
    Status.registration_keyEnter.value: utils.Registration.registration_enterKey,
    Status.registration_commandName.value: utils.Registration.registration_commandName,
    Status.registration_captainName.value: utils.Registration.registration_captainName,
    Status.registration_captainPhoneNumber.value: utils.Registration.registration_captainPhoneNumber,
    Status.registration_teammateName.value: utils.Registration.registration_teammateName,
    Status.registration_Verification.value: utils.Registration.registration_registrationVerification,
    Status.quest_keyEnter.value: utils.Quest.quest_keyEnter,
}