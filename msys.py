import urllib.request, json 
import sys, json
import subprocess
import requests
import os
from bs4 import BeautifulSoup
from pathlib import Path
import shutil

def url_is_valid(url):
    return requests.head(url) == 200

def page_of(name):
    return "https://packages.msys2.org/package/"+name

def download_page(url):
    try:
        request = requests.get(url)
        text = request.text
        return text
    except Exception as e:
        print("Error" , e)
        return ""

def package_exists(package):
    return "Package doesn't exist" not in download_page(page_of(package))
  
def get_all_links(url):
    soup = BeautifulSoup(download_page(url), 'html.parser') 
    urls = []
    for link in soup.find_all('a'):
        urls.append(link.get('href'))
    return urls

def all_possible_package_names(name):
    return [name , name+"-git"]

def get_download_link(package_full_name):
    for name in all_possible_package_names(package_full_name):
        links = get_all_links(page_of(name))
        for link in links:
            if str(link).find("https://mirror.msys2.org/mingw/mingw64/")!=-1 and str(link).find(".pkg.tar.zst")!=-1:
                print("Binary Package Found At: " , link)
                return link
    return ""

def download_and_extract(name , dir):
    return subprocess.Popen("wget -qO- --show-progress " + name + " | tar --zstd -xf - -C " + dir , shell=True).wait()


HOME = os.environ["HOME"]
packages = set()

# root = HOME+"/.msys/root"
# output = ""

options = {
    "--root":HOME+"/.msys/root",
    "--output":os.getcwd(),
    "--class":"Windows",
    "--package":"windows",
    "--name":"output.jar"
}

def dll_output_folder():
    return "win"

def dll_output_folder_full_path():
    return options["--output"]+"/"+dll_output_folder()

installed_packages = set()
failed_packages = set()
def installed_packages_file(): 
    return Path(options["--root"]+"/.installed_packages")

command = "help"
app_name = "msys.py"

def print_help():
    print("""usage: """+ app_name+""" [options] command [packages]
commands:
    install\tinstall a package or multiple packages
    remove\tremove a package or multiple packages
    fix\tfix partially installed packages
    java\tprint java library extractor for libraries included in given packages
    jar\tbundle given libraries in a jar along with the library extractor java file
    dll\tprints path of dlls in specified packages, or all packages if none is specified.
options:
    --root\tset path for packages download, by default it's set to ~/.msys/root
    --output\tset path for output, by default it's set to current directory
    --class\tset class name of the java file, by default it's Windows.
    --package\tset package name for the java source file, by default it's windows
    --name\tset name of the jar file""")

def process_cmd_options():
    global options
    for option in options.keys():
        if option in sys.argv:
            index = sys.argv.index(option)+1
            if index < len(sys.argv):
                options[option] = sys.argv[index]        
                sys.argv.remove(option)
                sys.argv.remove(options[option])

def process_cmd_args():
    global app_name
    global command

    app_name = sys.argv[0]

    if len(sys.argv) == 1:
        print_help()
        sys.exit()
    
    command = sys.argv[1]
    process_cmd_options()
    # print(command)
    # sys.argv.remove(command)
    # print(command)

    for arg in sys.argv[2:]:
        packages.add(arg)

def init():
    if not Path(options["--root"]).exists():
        os.makedirs(options["--root"])

    if installed_packages_file().exists():
        for pkg in installed_packages_file().read_text().splitlines():
            installed_packages.add(pkg.strip())

def package_installation_path(package):
    return options["--root"]+"/"+package

def package_info_file(package):
    with open(package_installation_path(package)+"/.PKGINFO","r") as file:
        return file.read()

packages_already_dealt_with = set()

def get_dependencies(package):
    dependencies = []
    for line in package_info_file(package).splitlines():
        tokens = line.split("=")
        if(len(tokens) >= 2 and  tokens[0].strip() == "depend"):
            dependencies.append(tokens[1].strip().replace(">","").replace("<",""))
    return dependencies

def install_deps(package , silent=False):
    deps = get_dependencies(package)
    if deps:
        if not silent: print("\tdepends on:")
        for dep in deps:
            if not silent: print("\t\t",package)
            install_package(dep , silent) 

def install_package(package , silent=False):
    """
    Installs a package alongside its dependencies or fixes incomplete installations.
    returns True on success (even if one of the dependencies failed) and False otherwise
    """
    if package in packages_already_dealt_with:
        return
    
    if package not in installed_packages:
        installation_path = package_installation_path(package)
        if Path(installation_path).is_dir():
            shutil.rmtree(installation_path)
        os.makedirs(installation_path)
        success = download_and_extract(get_download_link(package) , installation_path)
        if success != 0:
            # print("Error downloading package: " , package)
            failed_packages.add(package)
            return False

    installed_packages.add(package)
    packages_already_dealt_with.add(package) 
    #install_deps(package , silent) 
    deps = get_dependencies(package)
    if deps:
        if not silent: print("\tdepends on:")
        for dep in deps:
            if not silent: print("\t\t",package)
            install_package(dep , silent) 

    return True        



def remove_package(package):
    if package in installed_packages:
        installed_packages.remove(package)
        shutil.rmtree(package_installation_path(package))

def if_no_packages_exit():
    if(len(packages) < 1):
        print("Please specify a package or a number of packages")
        sys.exit()

def print_report(operation = "install"):
    if failed_packages:
        print("Failed to" , operation , len(failed_packages) , "packages")
        for pkg in failed_packages:
            print("\t",pkg)

def install_packages():
    if_no_packages_exit()
    for package in packages:
        if not package_exists(package):
            print("Package '"+package+"' not found")
            sys.exit(1)
        if package in installed_packages:
            print("Package '"+package+"' already installed")
        else:
            print("Installing: " + package)
            if not install_package(package):
                print("Failed to install '"+package+"'")
    print_report()

def remove_packages():
    available_packages = os.listdir(options["--root"])
    for package in packages:
        if package in available_packages:
            print("Removing '"+package+"'")
            remove_package(package)    
        else:
            print("Package '"+package+"' doesn't exist")

def fix():
    global packages
    if len(packages) == 0:
        for package in os.listdir(options["--root"]):
            if Path(package_installation_path(package)).is_dir(): 
                print("Fixing '"+package+"':")
                install_package(package , silent=True)  
    else:
        for package in packages:
            install_package(package , silent=True)
        
    print_report("fix")

def get_all_dependencies_of_a_package(package , packages_already_dealt_with=set()):
    if package in packages_already_dealt_with:
        return []
    packages_already_dealt_with.add(package)
    deps = get_dependencies(package)
    for dep in deps:
        deps.extend(get_all_dependencies_of_a_package(dep , packages_already_dealt_with))  

    return deps


def get_all_dependencies_of_packages(packages):
    deps = set()
    for package in packages:
        deps.update(get_all_dependencies_of_a_package(package))
    return deps
# def add_dependencies_to_packages():
#     global packages

#     deps = []
#     for package in packages:
#         deps.extend(get_dependencies(package))           
#         packages_already_dealt_with.add(package)
   
#     packages.update(deps)
#     if package not in packages_already_dealt_with:
#         add_dependencies_to_packages()      


def get_dll_paths(packages):
    dlls = []
    for package in packages:
        bin_dir = package_installation_path(package)+"/mingw64/bin"
        if Path(bin_dir).is_dir():
            for file in os.listdir(bin_dir):
                name, extension = os.path.splitext(file)
                #print("Name = ",name , "Extension = " , extension)
                if extension == ".dll":
                    dlls.append(bin_dir+"/"+file)

    return dlls

def print_dlls_paths():
    global packages
    if not packages:
        packages = [pkg for pkg in os.listdir(options["--root"]) if Path(options["--root"]+"/"+pkg).is_dir()]
    
    # add_dependencies_to_packages()
    packages.update(get_all_dependencies_of_packages(packages))

    for dll_path in get_dll_paths(packages):
        print(dll_path)


def export_jar(tmp_folder=options["--output"]+"/.tmp"):
    install_packages()
    packages.update(get_all_dependencies_of_packages(packages))
    if Path(tmp_folder).is_dir(): shutil.rmtree(tmp_folder)
    os.mkdir(tmp_folder)
    os.chdir(tmp_folder)
    
    java_source_path = options["--class"]+".java"
    Path(java_source_path).write_text(get_java_source(packages))
    subprocess.Popen("javac "+java_source_path, shell=True).wait()
    os.remove(java_source_path)

    os.mkdir("win")
    
    for dll_path in get_dll_paths(packages):
        shutil.copy(dll_path , dll_output_folder())
    
    jar_command = "jar cf "+options["--name"]+" "+"win "+options["--class"]+".class"

    print(jar_command)
    subprocess.Popen(jar_command, shell=True).wait()

    shutil.copy(options["--name"] , options["--output"])

    os.chdir(options["--output"])
    shutil.rmtree(tmp_folder)


def save_installed_packages():
    installed_packages_file().write_text("\n".join(installed_packages))

def get_dlls_as_java_array(packages):
    arr = ""
    for dll in get_dll_paths(packages):
        arr += "\t\t\""+"/"+os.path.basename(dll)+"\",\n"
    return arr

def get_java_source(packages):
    return """package """+options["--package"]+""";

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Locale;

public class """ +options["--class"] + """ {
    public static void extractResource(String resource_path , String filesystem_path) throws IOException {
        System.out.println("Looking for resource: "+resource_path);
        InputStream input = """ +options["--class"]+ """.class.getResourceAsStream(resource_path);
        FileOutputStream output = new FileOutputStream(filesystem_path);
        byte[] buf = new byte[256];
        int read = 0;
        while ((read = input.read(buf)) > 0) {
          output.write(buf, 0, read);
        }   
        output.close(); 
    }
    public static void extract_windows_libraries(String APP_NAME){
        String TEMP_DIR = System.getProperty("java.io.tmpdir") + APP_NAME;
        boolean all_libs_extracted = true;
        new File(TEMP_DIR).mkdirs();
        for(var lib : windows_libraries) {
            try{
                extractResource("/""" + dll_output_folder() + """/"+lib, TEMP_DIR+"/"+lib);
                System.out.println("Extracted "+lib+"to "+TEMP_DIR);
            }catch(Exception e){
                e.printStackTrace();
                all_libs_extracted = false;
                System.out.println("Error");
                break;
            }
        }
        if(all_libs_extracted){
            System.setProperty("jna.library.path", TEMP_DIR);
        }
    }

    private static final String [] windows_libraries = {
"""+ get_dlls_as_java_array(packages) +"""\t};
}
"""

def print_java_source_file():
    global packages
    print(get_java_source(packages))   

commands = {
    "install":install_packages,
    "remove":remove_packages,
    "fix":fix,
    "java":print_java_source_file,
    "jar":export_jar,
    "help":print_help,
    "dll":print_dlls_paths,
}

def main():

    process_cmd_args()
    init()

    if command not in commands.keys():
        print("Invalid command: '" , command , "' use help to see available commands.")
        sys.exit()
    
    commands[command]()
    save_installed_packages()


if __name__=="__main__":

    main()

# Example Package Names:
# mingw-w64-x86_64-gtk4
# mingw-w64-x86_64-gcc-libs
# mingw-w64-x86_64-glib2