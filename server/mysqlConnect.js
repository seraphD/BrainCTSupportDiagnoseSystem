var mysql      = require('mysql');
var connection = mysql.createPool({
  host     : 'localhost',
  // MySQL username
  user     : '',
  // MySQL user password
  password : '',
  database : 'medicalsupportsystem',
  connectionLimit : 100,
});

module.exports = connection;