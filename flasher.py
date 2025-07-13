#!/usr/bin/env python3

import os
import sys
import glob
import time
import subprocess
import argparse

def find_esp32_devices():
    """Encontra todos os dispositivos ESP32 conectados."""
    if sys.platform == 'darwin':  # macOS
        devices = glob.glob('/dev/cu.usbserial*')
        if not devices:
            # Tenta outros padrões comuns no macOS
            devices = glob.glob('/dev/tty.usbserial*')
    elif sys.platform == 'linux':
        devices = glob.glob('/dev/ttyUSB*')
    elif sys.platform == 'win32':
        import serial.tools.list_ports
        devices = [p.device for p in serial.tools.list_ports.comports()]
    else:
        raise OSError(f"Sistema operacional não suportado: {sys.platform}")
    
    return devices

def run_esptool_command(args, timeout=300):
    """Executa um comando esptool usando subprocess e mostra o progresso em tempo real."""
    cmd = ["esptool.py"] + args
    print(f"Executando comando: {' '.join(cmd)}")
    
    try:
        # Inicia o processo
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Redireciona stderr para stdout
            text=True,
            bufsize=1  # Linha por linha
        )
        
        # Lê e exibe a saída em tempo real
        for line in iter(process.stdout.readline, ''):
            print(line, end='')  # end='' porque a linha já tem \n
        
        # Espera o processo terminar
        process.stdout.close()
        return_code = process.wait()
        
        if return_code != 0:
            print(f"Comando falhou com código de retorno: {return_code}")
            return False
        
        return True
    except Exception as e:
        print(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

def erase_flash(device, baud_rate=115200):
    """Limpa toda a flash do dispositivo ESP32."""
    print(f"\n{'='*37}")
    print(f"Limpando flash do dispositivo: {device}")
    print(f"{'='*37}")
    
    args = ["--chip", "esp32", "--port", device, "--baud", str(baud_rate), "erase_flash"]
    return run_esptool_command(args)

def upload_platformio_style(device, firmware_dir, baud_rate=115200):
    """Faz upload do firmware no estilo PlatformIO."""
    print(f"\n{'='*37}")
    print(f"Fazendo upload do firmware para: {device}")
    print(f"{'='*37}")
    
    # Verifica se os arquivos necessários existem
    bootloader_path = os.path.join(firmware_dir, "bootloader.bin")
    partitions_path = os.path.join(firmware_dir, "partitions.bin")
    firmware_path = os.path.join(firmware_dir, "firmware.bin")
    
    if not os.path.exists(bootloader_path):
        print(f"Erro: bootloader.bin não encontrado em {firmware_dir}")
        return False
    
    if not os.path.exists(partitions_path):
        print(f"Erro: partitions.bin não encontrado em {firmware_dir}")
        return False
    
    if not os.path.exists(firmware_path):
        print(f"Erro: firmware.bin não encontrado em {firmware_dir}")
        return False
    
    # Constrói o comando para fazer upload de todos os arquivos
    args = [
        "--chip", "esp32",
        "--port", device,
        "--baud", str(baud_rate),
        "--before", "default_reset",
        "--after", "hard_reset",
        "write_flash",
        "-z",
        "--flash_mode", "dio",
        "--flash_freq", "40m",
        "--flash_size", "detect",
        "0x1000", bootloader_path,
        "0x8000", partitions_path,
        "0x10000", firmware_path
    ]
    
    return run_esptool_command(args)

def verify_firmware(device, firmware_dir, baud_rate=115200):
    """Verifica se o firmware foi carregado corretamente."""
    print(f"\n{'='*37}")
    print(f"Verificando firmware em: {device}")
    print(f"{'='*37}")
    
    # Verifica se os arquivos necessários existem
    bootloader_path = os.path.join(firmware_dir, "bootloader.bin")
    partitions_path = os.path.join(firmware_dir, "partitions.bin")
    firmware_path = os.path.join(firmware_dir, "firmware.bin")
    
    # Constrói o comando para verificar todos os arquivos
    args = [
        "--chip", "esp32",
        "--port", device,
        "--baud", str(baud_rate),
        "verify_flash",
        "0x1000", bootloader_path,
        "0x8000", partitions_path,
        "0x10000", firmware_path
    ]
    
    return run_esptool_command(args)

def main():
    parser = argparse.ArgumentParser(description='Ferramenta para limpar e programar ESP32')
    parser.add_argument('--firmware-dir', type=str, help='Diretório contendo os arquivos de firmware (bootloader.bin, partitions.bin, firmware.bin)')
    parser.add_argument('--erase-only', action='store_true', help='Apenas limpar a flash, sem fazer upload')
    parser.add_argument('--verify', action='store_true', help='Verificar o firmware após o upload')
    parser.add_argument('--baud', type=int, default=115200, help='Baud rate para comunicação (padrão: 115200)')
    parser.add_argument('--skip-erase', action='store_true', help='Pular a etapa de limpeza da flash')
    args = parser.parse_args()
    
    # Verifica o diretório de firmware se não estiver no modo apenas-limpar
    if not args.erase_only:
        if args.firmware_dir is None:
            print("Erro: Diretório de firmware não especificado.")
            print("Use --firmware-dir CAMINHO ou --erase-only para apenas limpar.")
            sys.exit(1)
        
        if not os.path.isdir(args.firmware_dir):
            print(f"Erro: Diretório de firmware não encontrado: {args.firmware_dir}")
            sys.exit(1)
        
        # Verifica se os arquivos necessários existem
        bootloader_path = os.path.join(args.firmware_dir, "bootloader.bin")
        partitions_path = os.path.join(args.firmware_dir, "partitions.bin")
        firmware_path = os.path.join(args.firmware_dir, "firmware.bin")
        
        if not os.path.exists(bootloader_path):
            print(f"Erro: bootloader.bin não encontrado em {args.firmware_dir}")
            sys.exit(1)
        
        if not os.path.exists(partitions_path):
            print(f"Erro: partitions.bin não encontrado em {args.firmware_dir}")
            sys.exit(1)
        
        if not os.path.exists(firmware_path):
            print(f"Erro: firmware.bin não encontrado em {args.firmware_dir}")
            sys.exit(1)
        
        print(f"Diretório de firmware: {args.firmware_dir}")
        print(f"Bootloader: {os.path.getsize(bootloader_path)} bytes")
        print(f"Partitions: {os.path.getsize(partitions_path)} bytes")
        print(f"Firmware: {os.path.getsize(firmware_path)} bytes ({os.path.getsize(firmware_path)/1024:.1f} KB)")
    
    # Encontra dispositivos ESP32
    devices = find_esp32_devices()
    
    if not devices:
        print("Nenhum dispositivo ESP32 encontrado.")
        sys.exit(1)
    
    print(f"Encontrados {len(devices)} dispositivos ESP32:")
    for i, device in enumerate(devices, 1):
        print(f"{i}. {device}")
    
    # Confirmação do usuário
    if args.skip_erase:
        action = "programar" if not args.erase_only else "não fazer nada"
    else:
        action = "limpar e programar" if not args.erase_only else "limpar"
    
    if args.verify and not args.erase_only:
        action += " e verificar"
    
    confirm = input(f"\nDeseja {action} todos os {len(devices)} dispositivos? (s/n): ")
    
    if confirm.lower() != 's':
        print("Operação cancelada pelo usuário.")
        sys.exit(0)
    
    # Processa cada dispositivo
    processed = 0
    failed = 0
    
    for device in devices:
        try:
            # Limpa a flash se não estiver pulando essa etapa
            if not args.skip_erase:
                if erase_flash(device, args.baud):
                    print("Flash limpa com sucesso!")
                    
                    # Aguarda o dispositivo reiniciar
                    print("Aguardando dispositivo reiniciar...")
                    time.sleep(5)  # Aumentado para 5 segundos
                else:
                    print(f"Falha ao limpar flash do dispositivo {device}")
                    failed += 1
                    continue
            
            # Faz upload do firmware se necessário
            if not args.erase_only:
                print("Iniciando upload do firmware...")
                if upload_platformio_style(device, args.firmware_dir, args.baud):
                    print(f"Upload do firmware concluído com sucesso para {device}!")
                    
                    # Aguarda o dispositivo reiniciar
                    print("Aguardando dispositivo reiniciar...")
                    time.sleep(5)
                    
                    # Verifica o firmware se solicitado
                    if args.verify:
                        print("Verificando o firmware...")
                        if verify_firmware(device, args.firmware_dir, args.baud):
                            print(f"Verificação do firmware concluída com sucesso para {device}!")
                            processed += 1
                        else:
                            print(f"Falha na verificação do firmware para {device}!")
                            failed += 1
                    else:
                        processed += 1
                else:
                    print(f"Falha no upload do firmware para {device}!")
                    failed += 1
            else:
                processed += 1
        except Exception as e:
            print(f"Erro ao processar dispositivo {device}: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
    
    # Relatório final
    print("\nProcesso concluído.")
    print(f"Dispositivos processados com sucesso: {processed}")
    print(f"Dispositivos com falha: {failed}")
    print(f"Total de dispositivos: {len(devices)}")

if __name__ == "__main__":
    main()