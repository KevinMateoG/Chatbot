const pool = require('./SecretConfig');

function testConnection() {
        let res = pool.query('SELECT nombre FROM prueba'); // Consulta a la base de datos
        console.log('Conexión exitosa:', res.row);
    
    }

testConnection();