# Banco Macro Scraper

Un scraper automatizado para monitorear el saldo de tu cuenta de Banco Macro y recibir notificaciones por email cuando supere un monto determinado.

## Configuración

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

3. Ejecutar el scraper:
```bash
python bank_scraper.py           # Modo headless (sin ventana)
python bank_scraper.py --debug   # Modo debug (con ventana visible)
```

## Variables de Entorno

- `BANK_URL`: URL del banco (https://www.macro.com.ar/bancainternet/)
- `BANK_USERNAME`: Tu usuario del banco
- `BANK_PASSWORD`: Tu contraseña del banco
- `THRESHOLD_AMOUNT`: Monto mínimo para enviar notificación (puede ser negativo)
- `EMAIL_FROM`: Email desde el cual enviar notificaciones
- `EMAIL_PASSWORD`: Contraseña de aplicación de Gmail (16 caracteres)
- `EMAIL_TO`: Email destino para notificaciones

## Configuración de Gmail

1. Activar autenticación de 2 factores en tu cuenta Gmail
2. Ir a https://myaccount.google.com/apppasswords
3. Crear una contraseña de aplicación para "Mail"
4. Usar esa contraseña de 16 caracteres en `EMAIL_PASSWORD`

## Funcionamiento

El scraper:
1. Abre Chrome y navega a Banco Macro
2. Hace login en dos pasos (usuario → contraseña)
3. Busca el saldo en el elemento `td[headers="_Saldo disponible"]`
4. Compara con el threshold configurado
5. Envía notificación por email si el saldo es mayor

## Scripts de Prueba

- `test_email.py`: Prueba solo el envío de emails
- `test_simple.py`: Prueba navegación básica
- `debug_scraper.py`: Encuentra elementos de login
- `verify_credentials.py`: Verifica formato de credenciales

## Seguridad

- Nunca compartas tu archivo `.env`
- Usa contraseñas de aplicación para Gmail
- Ejecuta en un entorno seguro
- Las credenciales se cargan desde variables de entorno