-- phpMyAdmin SQL Dump
-- version 4.2.12deb2+deb8u5
-- http://www.phpmyadmin.net
--
-- Хост: localhost
-- Время создания: Июн 12 2019 г., 18:17
-- Версия сервера: 5.5.62-0+deb8u1
-- Версия PHP: 5.6.40-0+deb8u2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- База данных: `wocd_dev_db`
--

-- --------------------------------------------------------

--
-- Структура таблицы `classes`
--

CREATE TABLE IF NOT EXISTS `classes` (
`id` int(11) NOT NULL,
  `class` varchar(255) NOT NULL,
  `reg_key` varchar(50) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `commands_list`
--

CREATE TABLE IF NOT EXISTS `commands_list` (
`id` int(11) NOT NULL,
  `command` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `respond_text` varchar(255) CHARACTER SET utf8mb4 NOT NULL,
  `respond_button_markup` varchar(2555) CHARACTER SET utf8mb4 NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `commands_list`
--

INSERT INTO `commands_list` (`id`, `command`, `respond_text`, `respond_button_markup`) VALUES
(1, '/menu', 'Ось ваше меню:', 'eydrZXlib2FyZCc6W1t7J3RleHQnOifQoNC10ZTRgdGC0YDQsNGG0ZbRjyDinI/vuI8nfSx7J3RleHQnOifQotC10YXQvdC+INC60LLQtdGB0YIg8J+Oryd9LHsndGV4dCc6J9Ce0YLRgNC40LzQsNGC0Lgg0LrRgNC+0YHQstC+0YDQtCDwn46yJ31dLFt7J3RleHQnOifQotCw0LHQu9C40YbRjyDRgNC10LnRgtC40L3Qs9GW0LIg8J+PhSd9LHsndGV4dCc6J9CU0L7QstGW0LTQutCwIOKdkyd9XSxbeyd0ZXh0Jzon0JLQuNC60LvRjtGH0LjRgtC4INC80LXQvdGOIPCfkb4nfV1dLCdyZXNpemVfa2V5Ym9hcmQnOlRydWUsJ29uZV90aW1lX2tleWJvYXJkJzpGYWxzZX0='),
(2, '/start', 'Привіт, Я - бот WOCD. Ось вам меню з доступним функціоналом:', 'eydrZXlib2FyZCc6W1t7J3RleHQnOifQoNC10ZTRgdGC0YDQsNGG0ZbRjyDinI/vuI8nfSx7J3RleHQnOifQotC10YXQvdC+INC60LLQtdGB0YIg8J+Oryd9LHsndGV4dCc6J9Ce0YLRgNC40LzQsNGC0Lgg0LrRgNC+0YHQstC+0YDQtCDwn46yJ31dLFt7J3RleHQnOifQotCw0LHQu9C40YbRjyDRgNC10LnRgtC40L3Qs9GW0LIg8J+PhSd9LHsndGV4dCc6J9CU0L7QstGW0LTQutCwIOKdkyd9XSxbeyd0ZXh0Jzon0JLQuNC60LvRjtGH0LjRgtC4INC80LXQvdGOIPCfkb4nfV1dLCdyZXNpemVfa2V5Ym9hcmQnOlRydWUsJ29uZV90aW1lX2tleWJvYXJkJzpGYWxzZX0='),
(3, 'Виключити меню 👾', 'Меню закрито, щоби знову побачити меню напишіть /menu', 'eydyZW1vdmVfa2V5Ym9hcmQnOlRydWV9');

-- --------------------------------------------------------

--
-- Структура таблицы `members`
--

CREATE TABLE IF NOT EXISTS `members` (
`id` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `is_capitan` tinyint(1) NOT NULL,
  `chat_id` varchar(255) DEFAULT NULL,
  `phone_number` varchar(255) DEFAULT NULL
) ENGINE=InnoDB AUTO_INCREMENT=161 DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `settings`
--

CREATE TABLE IF NOT EXISTS `settings` (
`id` int(11) NOT NULL,
  `attribute` varchar(255) NOT NULL,
  `value` varchar(255) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;

--
-- Дамп данных таблицы `settings`
--

INSERT INTO `settings` (`id`, `attribute`, `value`) VALUES
(1, 'num_of_members', '8');

-- --------------------------------------------------------

--
-- Структура таблицы `team_list`
--

CREATE TABLE IF NOT EXISTS `team_list` (
`id` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `class_id` varchar(10) NOT NULL,
  `captain_id` varchar(255) NOT NULL,
  `members_id` varchar(255) DEFAULT NULL
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Структура таблицы `users_status`
--

CREATE TABLE IF NOT EXISTS `users_status` (
`id` int(11) NOT NULL,
  `chat_id` varchar(255) NOT NULL,
  `status` varchar(255) NOT NULL,
  `team_id` int(255) DEFAULT NULL
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4;

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `classes`
--
ALTER TABLE `classes`
 ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `commands_list`
--
ALTER TABLE `commands_list`
 ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `members`
--
ALTER TABLE `members`
 ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `settings`
--
ALTER TABLE `settings`
 ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `team_list`
--
ALTER TABLE `team_list`
 ADD PRIMARY KEY (`id`);

--
-- Индексы таблицы `users_status`
--
ALTER TABLE `users_status`
 ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `classes`
--
ALTER TABLE `classes`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT для таблицы `commands_list`
--
ALTER TABLE `commands_list`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=7;
--
-- AUTO_INCREMENT для таблицы `members`
--
ALTER TABLE `members`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=161;
--
-- AUTO_INCREMENT для таблицы `settings`
--
ALTER TABLE `settings`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT для таблицы `team_list`
--
ALTER TABLE `team_list`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=26;
--
-- AUTO_INCREMENT для таблицы `users_status`
--
ALTER TABLE `users_status`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=9;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
