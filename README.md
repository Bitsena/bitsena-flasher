# BITSENA Firmware Uploader

Uma ferramenta robusta para limpar e programar dispositivos com o firmware do BITSENA.

## Desenvolvido por

**Vilmo Oliveira de Paula Júnior**  
Email: junior.vopj@gmail.com  
GitHub: [juniorVOPJ](https://github.com/juniorVOPJ)

## Descrição

Esta ferramenta foi desenvolvida para facilitar o processo de limpeza e programação em massa de dispositivos com o firmware BITSENA. Ela permite:

- Detectar automaticamente dispositivos conectados
- Limpar completamente a memória flash
- Fazer upload do firmware no estilo PlatformIO (bootloader, partições e firmware principal)
- Verificar a integridade do firmware após o upload
- Processar múltiplos dispositivos em sequência

## Requisitos

- Python 3.6 ou superior
- Biblioteca `esptool`
- Biblioteca `pyserial`

## Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/Bitsena/bitsena-flasher.git
   cd bitsena-flasher
   ```
2. Crie e ative um ambiente virtual Python:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ````
## Uso

### Limpar e programar dispositivos
```bash
python upload.py --firmware-dir /caminho/para/diretorio/build/firmware --baud 460800
```
Onde /caminho/para/diretorio/build/firmware é o diretório que contém os arquivos bootloader.bin, partitions.bin e firmware.bin.

### Apenas limpar a memória flash
```bash
python upload.py --erase-only
```

### Limpar, programar e verificar
```bash
python upload.py --firmware-dir /caminho/para/diretorio/build/firmware --verify
```

### Usar uma taxa de transmissão específica
```bash
python upload.py --firmware-dir /caminho/para/diretorio/build/firmware --baud 921600
```

## Opções
| Opção | Descrição |
|-------|-----------|
| `--firmware-dir PATH` | Diretório contendo os arquivos de firmware (bootloader.bin, partitions.bin, firmware.bin) |
| `--erase-only` | Apenas limpar a flash, sem fazer upload |
| `--verify` | Verificar o firmware após o upload |
| `--baud RATE` | Taxa de transmissão para comunicação (padrão: 115200) |
| `--skip-erase` | Pular a etapa de limpeza da flash (não recomendado) |

## Notas
- Recomenda-se sempre limpar completamente a flash antes de fazer upload do firmware para evitar problemas com dados residuais.
- Para dispositivos em massa, uma taxa de transmissão de 460800 oferece um bom equilíbrio entre velocidade e confiabilidade.
- Certifique-se de que os drivers USB-Serial estão instalados corretamente para seu sistema operacional.

## Licença
Este projeto é licenciado sob a licença MIT
