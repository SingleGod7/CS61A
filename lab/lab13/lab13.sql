.read data.sql


CREATE TABLE bluedog AS
  SELECT color ,pet FROM students
        WHERE color = 'blue' and pet = 'dog' ;

CREATE TABLE bluedog_songs AS
  SELECT color ,pet, song FROM students
        WHERE color = 'blue' and pet = 'dog' ;


CREATE TABLE smallest_int_having AS
  SELECT time, smallest FROM students
        GROUP BY smallest HAVING COUNT(*) = 1;


CREATE TABLE matchmaker AS
  SELECT a.pet, a.song, a.color, b.color FROM students AS a,students AS b
        WHERE a.pet = b.pet and a.song = b.song and a.time < b.time;


CREATE TABLE sevens AS
  SELECT seven FROM students, numbers
        WHERE numbers.time = students.time and students.number = 7  and numbers.'7' = "True";

CREATE TABLE avg_difference AS
  SELECT round(avg(abs(number - smallest))) FROM students;

