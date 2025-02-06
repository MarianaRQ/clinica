-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 11-12-2024 a las 00:46:20
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `clinica`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clinicas`
--

CREATE TABLE `clinicas` (
  `Codigo_Postal` int(11) NOT NULL,
  `Numero` int(11) NOT NULL,
  `Calle` varchar(4) NOT NULL,
  `Ciudad` text NOT NULL,
  `Telefono` varchar(15) NOT NULL,
  `NumColegiado` varchar(12) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `clinicas`
--

INSERT INTO `clinicas` (`Codigo_Postal`, `Numero`, `Calle`, `Ciudad`, `Telefono`, `NumColegiado`) VALUES
(1, 2, '3', 'jajaj', '345453', '282'),
(12, 23, '56', 'jajaj', '0000', '34');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `medicooftamologico`
--

CREATE TABLE `medicooftamologico` (
  `NumColegiado` varchar(12) NOT NULL,
  `Nombre` text NOT NULL,
  `Fecha_Nac` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `medicooftamologico`
--

INSERT INTO `medicooftamologico` (`NumColegiado`, `Nombre`, `Fecha_Nac`) VALUES
('01', 'yoooppp', '2024-05-18'),
('282', 'yuuu', '2024-12-11'),
('34', 'kakka', '2024-12-10'),
('90', 'Mariana', '2024-12-12');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pacientes`
--

CREATE TABLE `pacientes` (
  `Dni` varchar(12) NOT NULL,
  `Nombre` text NOT NULL,
  `Fecha_Nac` date NOT NULL,
  `Direccion` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pacientes`
--

INSERT INTO `pacientes` (`Dni`, `Nombre`, `Fecha_Nac`, `Direccion`) VALUES
('8392200', 'Mariana', '2024-12-14', 'yo'),
('839403', 'Mari', '2024-12-24', 'jjajajjajaaakakakka'),
('839923', 'Gysel Mariana', '2024-12-14', 'yo'),
('9929292', 'aksks', '2024-12-10', 'yo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `periodo`
--

CREATE TABLE `periodo` (
  `Fecha_I` date NOT NULL,
  `Fecha_F` date NOT NULL,
  `NumColegiado` varchar(12) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `periodo`
--

INSERT INTO `periodo` (`Fecha_I`, `Fecha_F`, `NumColegiado`) VALUES
('2024-10-16', '2024-11-22', '01'),
('2024-12-19', '2024-12-25', '282'),
('2024-11-15', '2024-11-15', '90');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prueba`
--

CREATE TABLE `prueba` (
  `Codigo_Prueba` int(11) NOT NULL,
  `Nombre` text NOT NULL,
  `Fecha` date NOT NULL,
  `Hora` time NOT NULL,
  `Tipo` text NOT NULL,
  `Descripcion` varchar(255) NOT NULL,
  `Id` int(11) NOT NULL,
  `NumColegiado` varchar(12) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `idRoles` int(11) NOT NULL,
  `Descripcion` varchar(300) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tratamiento`
--

CREATE TABLE `tratamiento` (
  `Id` int(11) NOT NULL,
  `Nombre` text NOT NULL,
  `Fecha_Inicio` date NOT NULL,
  `NumColegiado` varchar(12) NOT NULL,
  `Dni` varchar(12) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `idusuarios` int(11) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `roles_idRoles` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `clinicas`
--
ALTER TABLE `clinicas`
  ADD PRIMARY KEY (`Codigo_Postal`,`Numero`,`Calle`),
  ADD UNIQUE KEY `NumColegiado` (`NumColegiado`);

--
-- Indices de la tabla `medicooftamologico`
--
ALTER TABLE `medicooftamologico`
  ADD PRIMARY KEY (`NumColegiado`);

--
-- Indices de la tabla `pacientes`
--
ALTER TABLE `pacientes`
  ADD PRIMARY KEY (`Dni`);

--
-- Indices de la tabla `periodo`
--
ALTER TABLE `periodo`
  ADD PRIMARY KEY (`Fecha_I`,`Fecha_F`),
  ADD UNIQUE KEY `NumColegiado` (`NumColegiado`);

--
-- Indices de la tabla `prueba`
--
ALTER TABLE `prueba`
  ADD PRIMARY KEY (`Codigo_Prueba`),
  ADD UNIQUE KEY `Id` (`Id`),
  ADD UNIQUE KEY `NumColegiado` (`NumColegiado`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`idRoles`);

--
-- Indices de la tabla `tratamiento`
--
ALTER TABLE `tratamiento`
  ADD PRIMARY KEY (`Id`),
  ADD UNIQUE KEY `NumColegiado` (`NumColegiado`),
  ADD UNIQUE KEY `Dni` (`Dni`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`idusuarios`),
  ADD UNIQUE KEY `roles_idRoles` (`roles_idRoles`);

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `clinicas`
--
ALTER TABLE `clinicas`
  ADD CONSTRAINT `clinicas_ibfk_1` FOREIGN KEY (`NumColegiado`) REFERENCES `medicooftamologico` (`NumColegiado`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `periodo`
--
ALTER TABLE `periodo`
  ADD CONSTRAINT `periodo_ibfk_1` FOREIGN KEY (`NumColegiado`) REFERENCES `medicooftamologico` (`NumColegiado`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `prueba`
--
ALTER TABLE `prueba`
  ADD CONSTRAINT `prueba_ibfk_1` FOREIGN KEY (`NumColegiado`) REFERENCES `medicooftamologico` (`NumColegiado`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `tratamiento`
--
ALTER TABLE `tratamiento`
  ADD CONSTRAINT `tratamiento_ibfk_1` FOREIGN KEY (`NumColegiado`) REFERENCES `medicooftamologico` (`NumColegiado`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `tratamiento_ibfk_2` FOREIGN KEY (`Dni`) REFERENCES `pacientes` (`Dni`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `tratamiento_ibfk_3` FOREIGN KEY (`Id`) REFERENCES `prueba` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`roles_idRoles`) REFERENCES `roles` (`idRoles`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
