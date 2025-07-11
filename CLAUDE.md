# Banco Macro Scraper - Claude Instructions

## Proyecto
Scraper automatizado para Banco Macro que monitorea saldo y envía notificaciones por email.

## Estructura
- `bank_scraper.py`: Script principal del scraper
- `test_email.py`: Prueba envío de emails
- `test_simple.py`: Prueba navegación básica
- `debug_scraper.py`: Debug de elementos web
- `verify_credentials.py`: Verifica formato de credenciales
- `check_2fa.py`: Guía para configurar 2FA
- `.env`: Variables de entorno (no versionar)
- `requirements.txt`: Dependencias de Python
- `README.md`: Documentación del proyecto

## Comandos útiles
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar scraper
python bank_scraper.py           # Modo headless
python bank_scraper.py --debug   # Modo debug con ventana

# Scripts de prueba
python test_email.py             # Prueba solo email
python test_simple.py            # Prueba navegación
python verify_credentials.py     # Verifica credenciales
```

## Configuración del banco
- URL: https://www.macro.com.ar/bancainternet/
- Login paso 1: input#textField1 (usuario) → button#processCustomerLogin
- Login paso 2: input#login_textField1 (contraseña) → button#processSystem_UserLogin
- Saldo: td[headers="_Saldo disponible"] (primer elemento)

## Configuración de Gmail
- Requiere 2FA activado
- Contraseña de aplicación de 16 caracteres
- SMTP: smtp.gmail.com:587 con STARTTLS

## Funcionamiento
1. Selenium abre Chrome (headless por defecto)
2. Navega a Banco Macro
3. Login en dos pasos con WebDriverWait
4. Busca saldo con selector CSS específico
5. Compara con threshold (puede ser negativo)
6. Envía email si saldo > threshold

## Notas de desarrollo
- Usar WebDriverWait para elementos dinámicos
- Manejo de errores robusto en cada paso
- Logs detallados para debugging
- Parsing de saldo con regex para números
- Chrome options optimizadas para WSL

## Seguridad
- Credenciales en .env (no versionar)
- Contraseñas de aplicación para Gmail
- Validación SSL/TLS automática
- User-Agent específico para evitar detección
- .gitignore completo protege datos sensibles

## Control de versiones
- Repositorio Git inicializado
- .env excluido del repositorio
- Archivos sensibles protegidos por .gitignore
- Commits con formato estándar

## Posibles mejoras futuras
- Programar ejecución automática (cron/Task Scheduler)
- Agregar más tipos de notificaciones (SMS, Slack, etc.)
- Implementar logs rotativos
- Agregar múltiples cuentas bancarias
- Crear interfaz web simple
- Agregar métricas de ejecución
- Implementar reintentos automáticos
- Agregar alertas por email si falla el scraper