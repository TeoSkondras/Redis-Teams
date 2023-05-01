CREATE SCHEMA `users_meetings` ;

use users_meetings;


CREATE TABLE `users_meetings`.`users` (
  `userID` INT NOT NULL,
  `name` VARCHAR(45) NULL,
  `age` INT NULL,
  `gender` VARCHAR(45) NULL,
  `email` VARCHAR(45) NULL,
  PRIMARY KEY (`userID`),
  UNIQUE INDEX `userID_UNIQUE` (`userID` ASC) VISIBLE);
  
INSERT INTO users (userID, name, age, gender, email) VALUES 
(1, 'John Smith', 25, 'Male', 'john.smith@example.com'),
(2, 'Jane Doe', 30, 'Female', 'jane.doe@example.com'),
(3, 'Mike Johnson', 40, 'Male', 'mike.johnson@example.com'),
(4, 'Sara Lee', 28, 'Female', 'sara.lee@example.com'),
(5, 'David Kim', 32, 'Male', 'david.kim@example.com'),
(6, 'Emily Chen', 27, 'Female', 'emily.chen@example.com'),
(7, 'James Brown', 45, 'Male', 'james.brown@example.com'),
(8, 'Megan Taylor', 29, 'Female', 'megan.taylor@example.com'),
(9, 'Chris Jackson', 38, 'Male', 'chris.jackson@example.com'),
(10, 'Linda Nguyen', 31, 'Female', 'linda.nguyen@example.com'),
(11, 'Michael Lee', 24, 'Male', 'michael.lee@example.com'),
(12, 'Sophia Rodriguez', 26, 'Female', 'sophia.rodriguez@example.com'),
(13, 'William Davis', 35, 'Male', 'william.davis@example.com'),
(14, 'Ava Martinez', 33, 'Female', 'ava.martinez@example.com'),
(15, 'Daniel Hernandez', 29, 'Male', 'daniel.hernandez@example.com'),
(16, 'Emma Wilson', 28, 'Female', 'emma.wilson@example.com'),
(17, 'Matthew Garcia', 41, 'Male', 'matthew.garcia@example.com'),
(18, 'Olivia Perez', 30, 'Female', 'olivia.perez@example.com'),
(19, 'Joseph Harris', 37, 'Male', 'joseph.harris@example.com'),
(20, 'Isabella Rivera', 25, 'Female', 'isabella.rivera@example.com'),
(21, 'Christopher King', 43, 'Male', 'christopher.king@example.com'),
(22, 'Chloe Green', 26, 'Female', 'chloe.green@example.com'),
(23, 'Andrew Lee', 39, 'Male', 'andrew.lee@example.com'),
(24, 'Madison Taylor', 27, 'Female', 'madison.taylor@example.com'),
(25, 'Joshua Brown', 36, 'Male', 'joshua.brown@example.com'),
(26, 'Emily Davis', 29, 'Female', 'emily.davis@example.com'),
(27, 'David Gonzalez', 42, 'Male', 'david.gonzalez@example.com'),
(28, 'Mia Lopez', 23, 'Female', 'mia.lopez@example.com'),
(29, 'Ryan Perez', 34, 'Male', 'ryan.perez@example.com'),
(30, 'Avery Smith', 28, 'Female', 'avery.smith@example.com');
  

CREATE TABLE `users_meetings`.`meetings` (
  `meetingID` INT NOT NULL,
  `title` VARCHAR(45) NULL,
  `description` VARCHAR(45) NULL,
  `isPublic` TINYINT NULL,
  `audience` VARCHAR(145) NULL,
  PRIMARY KEY (`meetingID`),
  UNIQUE INDEX `meetingID_UNIQUE` (`meetingID` ASC) VISIBLE);
  
  INSERT INTO meetings (meetingID, title, description, isPublic, audience) VALUES 
(1, 'Team Meeting', 'Weekly meeting to discuss progress', 1, ''),
(2, 'Product Launch', 'Meeting to plan product launch', 0, 'john.smith@example.com,jane.doe@example.com,mike.johnson@example.com'),
(3, 'Marketing Campaign', 'Meeting to discuss marketing campaign', 1, ''),
(4, 'Budget Review', 'Meeting to review budget', 0, 'sara.lee@example.com,david.kim@example.com,emily.chen@example.com'),
(5, 'Training Session', 'Training session for new employees', 1, ''),
(6, 'Client Meeting', 'Meeting with client to discuss project', 0, 'james.brown@example.com,megan.taylor@example.com,chris.jackson@example.com'),
(7, 'Performance Review', 'Meeting to conduct performance review', 1, ''),
(8, 'Brainstorming Session', 'Meeting to brainstorm new ideas', 0, 'linda.nguyen@example.com,michael.lee@example.com,sophia.rodriguez@example.com'),
(9, 'Project Kickoff', 'Meeting to kickoff new project', 1, ''),
(10, 'Vendor Negotiations', 'Meeting to negotiate with vendors', 0, 'ava.martinez@example.com,daniel.hernandez@example.com,emma.wilson@example.com'),
(11, 'Executive Meeting', 'Meeting with executives to discuss strategy', 1, ''),
(12, 'Team Building', 'Team building activity for employees', 0, 'matthew.garcia@example.com,olivia.perez@example.com,joseph.harris@example.com'),
(13, 'Quarterly Review', 'Meeting to conduct quarterly review', 1, ''),
(14, 'New Hire Orientation', 'Meeting to orient new hires', 0, 'isabella.rivera@example.com,christopher.king@example.com,chloe.green@example.com'),
(15, 'Project Status', 'Meeting to discuss project status', 1, ''),
(16, 'Department Meeting', 'Meeting with department members', 0, 'andrew.lee@example.com,madison.taylor@example.com,joshua.brown@example.com'),
(17, 'Company Picnic', 'Annual company picnic', 1, ''),
(18, 'Interviews', 'Meeting to conduct job interviews', 0, 'emily.davis@example.com,david.gonzalez@example.com,mia.lopez@example.com'),
(19, 'Training Needs Assessment', 'Meeting to assess training needs', 1, ''),
(20, 'Product Development', 'Meeting to discuss product development', 0, 'ryan.perez@example.com,avery.smith@example.com');


CREATE TABLE `users_meetings`.`meeting_instances` (
  `meetingID` INT NOT NULL,
  `orderID` INT NOT NULL,
  `fromdatetime` DATETIME NULL,
  `todatetime` DATETIME NULL,
  PRIMARY KEY (`meetingID`, `orderID`),
  UNIQUE INDEX `meetingID_UNIQUE` (`meetingID` ASC) VISIBLE,
  UNIQUE INDEX `orderID_UNIQUE` (`orderID` ASC) VISIBLE,
  CONSTRAINT `meetingID`
    FOREIGN KEY (`meetingID`)
    REFERENCES `users_meetings`.`meetings` (`meetingID`)
    ON DELETE CASCADE
    ON UPDATE RESTRICT);

-- Inserts for meeting instances of the first 5 meetings
INSERT INTO meeting_instances (meetingID, orderID, fromdatetime, todatetime)
VALUES 
  -- Meeting 1
  (1, 1, '2023-05-10 09:00:00', '2023-05-10 11:30:00'),
  (1, 2, '2023-05-10 13:00:00', '2023-05-10 15:30:00'),
  (1, 3, '2023-05-10 17:00:00', '2023-05-10 19:30:00'),
    -- Meeting 2
  (2, 1, '2023-05-11 09:00:00', '2023-05-11 11:30:00'),
  (2, 2, '2023-05-11 14:00:00', '2023-05-11 16:00:00'),
  (2, 3, '2023-05-11 18:00:00', '2023-05-11 20:30:00'),
  -- Meeting 3
  (3, 1, '2023-05-12 09:30:00', '2023-05-12 11:00:00'),
  (3, 2, '2023-05-12 14:00:00', '2023-05-12 16:30:00'),
  (3, 3, '2023-05-12 19:00:00', '2023-05-12 21:00:00'),
  -- Meeting 4
  (4, 1, '2023-05-13 10:00:00', '2023-05-13 12:00:00'),
  (4, 2, '2023-05-13 14:30:00', '2023-05-13 16:00:00'),
  (4, 3, '2023-05-13 18:00:00', '2023-05-13 20:00:00'),
  -- Meeting 5
  (5, 1, '2023-05-14 11:00:00', '2023-05-14 13:30:00'),
  (5, 2, '2023-05-14 15:00:00', '2023-05-14 17:30:00'),
  (5, 3, '2023-05-14 19:00:00', '2023-05-14 21:00:00');


CREATE SCHEMA `events_log` ;

use events_log;

CREATE TABLE `events_log`.`events_log` (
  `event_id` INT NOT NULL,
  `userID` INT NOT NULL,
  `event_type` VARCHAR(45) NULL,
  `timestamp` DATETIME NULL,
  PRIMARY KEY (`event_id`),
  UNIQUE INDEX `event_id_UNIQUE` (`event_id` ASC) VISIBLE);
