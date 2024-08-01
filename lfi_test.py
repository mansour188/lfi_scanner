import requests
from io import BytesIO
from colorama import Fore, init
import os

# Initialize Colorama
init(autoreset=True)

# Define color constants
GREEN_NORMAL = Fore.GREEN
RED_WARNING = Fore.RED
END = Fore.RESET

# Danger icon
DANGER_ICON = "⚠️"

def banner():
    print(Fore.LIGHTBLUE_EX + """
 █████      ███████████ █████                   █████████    █████████    █████████   ██████   █████
░░███      ░░███░░░░░░█░░███                   ███░░░░░███  ███░░░░░███  ███░░░░░███ ░░██████ ░░███ 
 ░███       ░███   █ ░  ░███                  ░███    ░░░  ███     ░░░  ░███    ░███  ░███░███ ░███ 
 ░██        ░███████    ░███     ██████████   ░░█████████ ░███          ░███████████  ░███░░███░███ 
 ░███       ░███░░░█    ░███    ░░░░░░░░░░     ░░░░░░░░███░███          ░███░░░░░███  ░███ ░░██████ 
 ░███ ░   █ ░███  ░     ░███                   ███    ░███░░███     ███ ░███    ░███  ░███  ░░█████ 
 ██████████ █████       █████                 ░░█████████  ░░█████████  █████   █████ █████  ░░█████
░░░░░░░░░░ ░░░░░       ░░░░░                   ░░░░░░░░░    ░░░░░░░░░  ░░░░░   ░░░░░ ░░░░░    ░░░░░ 
                                                       
┌─┐┬─┐┌─┐┌─┐┌┬┐┌─┐┌┬┐  ┌┐ ┬ ┬  ┌┐ ┌─┐┌┐┐  ┌─┐┬ ┬┌┬┐┌─┐┌┬┐  ┌┬┐┌─┐┌┐┐┌─┐┌─┐┬ ┬┬─┐  
│  ├┬┘├┤ ├─┤ │ ├┤  ││  ├┴┐└┬┘  ├┴┐├┤ │││  ├─┤├─┤│││├┤  ││  │││├─┤│││└─┐│ ││ │├┬┘  
└─┘┴└─└─┘┴ ┴ ┴ └─┘─┴┘  └─┘ ┴   └─┘└─┘┘└┘  ┴ ┴┴ ┴┴ ┴└─┘─┴┘  ┴ ┴┴ ┴┘└┘└─┘└─┘└─┘┴└─                                               
                                                                                                    
Simple LFI (Local File Inclusion) Vulnerability Scanner\n""" + Fore.RESET)

def read_lfi_paths(file_path):
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"{RED_WARNING}Error: File '{file_path}' not found.{END}")
        return []

def is_sensitive(content):
    sensitive_patterns = ['root:x:0:0:root', 'bin:x:1:1:bin', 'daemon:x:2:2:daemon', 'passwd', 'shadow', 'secret']
    return any(pattern in content for pattern in sensitive_patterns)

def display_file_content(file_content):
    lines = file_content.split('\n')
    first_lines = '\n'.join(lines[:3])
    last_lines = '\n'.join(lines[-3:])
    print(f"{RED_WARNING}{DANGER_ICON} Potential Sensitive Content Detected! {END}")
    print(f"{GREEN_NORMAL}First 3 lines:{END}\n{first_lines}")
    print(f"{GREEN_NORMAL}Last 3 lines:{END}\n{last_lines}")

def test_lfi(domain, lfi_paths):
    total_paths = len(lfi_paths)
    found_vulnerabilities = []

    for i, path in enumerate(lfi_paths):
        if not path.startswith('/'):
            path = '/' + path
        url = f"{domain}{path}"
        progress = (i + 1) / total_paths * 100
        print(f"\n[{progress:.2f}%] Testing: {url}")

        try:
            response = requests.get(url, stream=True)
            status_code = response.status_code
            content_type = response.headers.get('Content-Type', '')

            print(f"Status Code: {status_code}")
            print(f"Content-Type: {content_type}")

            if status_code == 200:
                if 'text/html' not in content_type:
                    file_content = BytesIO(response.content).getvalue().decode('utf-8', errors='ignore')

                    if is_sensitive(file_content):
                        found_vulnerabilities.append(url)
                        display_file_content(file_content)
                    else:
                        print(f"{GREEN_NORMAL}No obvious sensitive information found in file content: {url}{END}")
                else:
                    print(f"{GREEN_NORMAL}This path returns a webpage or non-file response: {url}{END}")

        except requests.RequestException as e:
            print(f"Error testing URL: {url} - {e}")

    # Print found vulnerabilities
    if found_vulnerabilities:
        print(Fore.LIGHTYELLOW_EX + "\nFound Vulnerabilities:" + END)
        for vuln in found_vulnerabilities:
            print(f"{RED_WARNING}{DANGER_ICON} Vulnerability Found: {vuln}{END}")
    else:
        print(f"{GREEN_NORMAL}No vulnerabilities found.{END}")

    # Print the closing banner
    print(Fore.LIGHTRED_EX + """
████████╗███████╗███████╗████████╗     ██████╗ ██████╗ ███╗   ██╗██████╗ ██╗     ███████╗████████╗███████╗   
╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝    ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██║     ██╔════╝╚══██╔══╝██╔════╝   
   ██║   █████╗  ███████╗   ██║       ██║     ██║   ██║██╔████╔██║██████╔╝██║     █████╗     ██║   █████╗     
   ██║   ██╔══╝  ╚════██║   ██║       ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝     ██║   ██╔══╝     
   ██║   ███████╗███████║   ██║       ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ███████╗███████╗   ██║   ███████╗██╗
   ╚═╝   ╚══════╝╚══════╝   ╚═╝        ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═╝
                                                                                                              
    ████████╗██╗  ██╗ █████╗ ███╗   ██╗██╗  ██╗    ██╗   ██╗ ██████╗ ██╗   ██╗██╗                             
    ╚══██╔══╝██║  ██║██╔══██╗████╗  ██║██║ ██╔╝    ╚██╗ ██╔╝██╔═══██╗██║   ██║██║                             
       ██║   ███████║███████║██╔██╗ ██║█████╔╝      ╚████╔╝ ██║   ██║██║   ██║██║                             
       ██║   ██╔══██║██╔══██║██║╚██╗██║██╔═██╗       ╚██╔╝  ██║   ██║██║   ██║██║                             
       ██║   ██║  ██║██║  ██║██║ ╚████║██║  ██╗      ██║   ╚██████╔╝╚██████╔╝███████╗                        
       ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝      ╚═╝    ╚═════╝   ╚═════╝ ╚══════╝                        
                                                                                                              
""" + END)

# Example usage
if __name__ == "__main__":
    banner()
    domain = input("Enter the domain to scan (e.g., http://example.com): ")
    lfi_paths = read_lfi_paths('list.list1')
    test_lfi(domain, lfi_paths)
