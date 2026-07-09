#!/usr/bin/env python3
"""
GearDevil - AppImage Installer & Uninstaller
"""

import os
import sys
import shutil
import subprocess
import tempfile
import re
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from threading import Thread


class GearDevil:
    def __init__(self, root):
        self.root = root
        self.root.title("GearDevil")
        self.root.geometry("480x520")
        self.root.resizable(False, False)
        
        self.bg_color = "#1e1e2e"
        self.fg_color = "#cdd6f4"
        self.accent_color = "#89b4fa"
        self.success_color = "#a6e3a1"
        self.error_color = "#f38ba8"
        self.card_bg = "#313244"
        self.warning_color = "#fab387"
        
        self.root.configure(bg=self.bg_color)
        
        self.home = Path.home()
        self.applications_dir = self.home / "Applications"
        self.icons_dir = self.home / ".local" / "share" / "icons"
        self.desktop_entries_dir = self.home / ".local" / "share" / "applications"
        
        self.applications_dir.mkdir(parents=True, exist_ok=True)
        self.icons_dir.mkdir(parents=True, exist_ok=True)
        self.desktop_entries_dir.mkdir(parents=True, exist_ok=True)
        
        self.selected_appimage = StringVar()
        self.app_name = StringVar()
        self.status_text = StringVar(value="Ready")
        self.installed_apps = []
        
        self.setup_ui()
        self.load_installed_apps()
    
    def setup_ui(self):
        header_frame = Frame(self.root, bg=self.bg_color)
        header_frame.pack(fill=X, pady=10, padx=15)
        
        title_label = Label(
            header_frame,
            text="⚙️ GearDevil",
            font=("Segoe UI", 20, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack(side=LEFT)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=15, pady=5)
        
        self.install_tab = Frame(self.notebook, bg=self.card_bg)
        self.notebook.add(self.install_tab, text="  Install  ")
        
        self.uninstall_tab = Frame(self.notebook, bg=self.card_bg)
        self.notebook.add(self.uninstall_tab, text="  Uninstall  ")
        
        self.setup_install_tab()
        self.setup_uninstall_tab()
        
        footer = Label(
            self.root,
            text="GearDevil v1.0",
            font=("Segoe UI", 8),
            bg=self.bg_color,
            fg="#6c7086"
        )
        footer.pack(pady=5)
    
    def setup_install_tab(self):
        tab = self.install_tab
        
        Label(
            tab,
            text="Select AppImage:",
            font=("Segoe UI", 10),
            bg=self.card_bg,
            fg=self.fg_color
        ).pack(anchor=W, padx=15, pady=(15, 3))
        
        file_frame = Frame(tab, bg=self.card_bg)
        file_frame.pack(fill=X, padx=15, pady=3)
        
        Entry(
            file_frame,
            textvariable=self.selected_appimage,
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg=self.fg_color,
            relief=FLAT,
            insertbackground=self.fg_color
        ).pack(side=LEFT, fill=X, expand=True, padx=(0, 8))
        
        Button(
            file_frame,
            text="Browse",
            command=self.browse_appimage,
            bg=self.accent_color,
            fg=self.bg_color,
            relief=FLAT,
            font=("Segoe UI", 9, "bold"),
            padx=10, pady=3
        ).pack(side=RIGHT)
        
        Label(
            tab,
            text="App Name (optional):",
            font=("Segoe UI", 10),
            bg=self.card_bg,
            fg=self.fg_color
        ).pack(anchor=W, padx=15, pady=(12, 3))
        
        Entry(
            tab,
            textvariable=self.app_name,
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg=self.fg_color,
            relief=FLAT,
            insertbackground=self.fg_color
        ).pack(fill=X, padx=15, pady=3)
        
        Button(
            tab,
            text="🚀 Install",
            command=self.start_installation,
            bg=self.accent_color,
            fg=self.bg_color,
            relief=FLAT,
            font=("Segoe UI", 11, "bold"),
            padx=20, pady=8
        ).pack(pady=15)
        
        self.progress = ttk.Progressbar(
            tab,
            mode='indeterminate',
            length=280
        )
        
        self.status_label = Label(
            tab,
            textvariable=self.status_text,
            font=("Segoe UI", 9),
            bg=self.card_bg,
            fg=self.fg_color,
            wraplength=430
        )
        self.status_label.pack(pady=5)
        
        log_frame = Frame(tab, bg=self.bg_color)
        log_frame.pack(fill=BOTH, expand=True, padx=15, pady=(10, 15))
        
        self.log_text = Text(
            log_frame,
            font=("Consolas", 8),
            bg=self.bg_color,
            fg=self.fg_color,
            relief=FLAT,
            height=12,
            state=DISABLED
        )
        self.log_text.pack(fill=BOTH, expand=True)
    
    def setup_uninstall_tab(self):
        tab = self.uninstall_tab
        
        Label(
            tab,
            text="Installed AppImages:",
            font=("Segoe UI", 10),
            bg=self.card_bg,
            fg=self.fg_color
        ).pack(anchor=W, padx=15, pady=(15, 5))
        
        list_frame = Frame(tab, bg=self.card_bg)
        list_frame.pack(fill=BOTH, expand=True, padx=15, pady=5)
        
        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.uninstall_listbox = Listbox(
            list_frame,
            font=("Segoe UI", 9),
            bg=self.card_bg,
            fg=self.fg_color,
            relief=FLAT,
            selectbackground=self.accent_color,
            selectforeground=self.bg_color,
            activestyle='none',
            yscrollcommand=scrollbar.set
        )
        self.uninstall_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.uninstall_listbox.yview)
        
        self.uninstall_listbox.bind('<<ListboxSelect>>', self.on_uninstall_select)
        
        self.selected_info = Label(
            tab,
            text="",
            font=("Segoe UI", 8),
            bg=self.card_bg,
            fg=self.warning_color,
            wraplength=430
        )
        self.selected_info.pack(pady=3)
        
        btn_frame = Frame(tab, bg=self.card_bg)
        btn_frame.pack(pady=10)
        
        Button(
            btn_frame,
            text="🗑️ Uninstall",
            command=self.start_uninstall,
            bg=self.error_color,
            fg=self.bg_color,
            relief=FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=15, pady=6
        ).pack(side=LEFT, padx=5)
        
        Button(
            btn_frame,
            text="🔄",
            command=self.load_installed_apps,
            bg=self.card_bg,
            fg=self.fg_color,
            relief=FLAT,
            font=("Segoe UI", 10),
            padx=10, pady=6
        ).pack(side=LEFT, padx=5)
    
    def make_executable(self, file_path):
        """Make a file executable (chmod +x)"""
        try:
            current_mode = os.stat(file_path).st_mode
            if not (current_mode & 0o111):
                os.chmod(file_path, 0o755)
                return True
            return False
        except Exception:
            return False
    
    def load_installed_apps(self):
        self.installed_apps = []
        self.uninstall_listbox.delete(0, END)
        
        if self.applications_dir.exists():
            for appimage in sorted(self.applications_dir.glob("*.AppImage")):
                desktop = self.find_desktop_entry_for_path(str(appimage))
                self.installed_apps.append({
                    'name': appimage.name,
                    'path': str(appimage),
                    'desktop': desktop
                })
            for appimage in sorted(self.applications_dir.glob("*.appimage")):
                desktop = self.find_desktop_entry_for_path(str(appimage))
                self.installed_apps.append({
                    'name': appimage.name,
                    'path': str(appimage),
                    'desktop': desktop
                })
        
        for app in self.installed_apps:
            self.uninstall_listbox.insert(END, f"📦 {app['name']}")
        
        if not self.installed_apps:
            self.uninstall_listbox.insert(END, "No AppImages installed")
    
    def find_desktop_entry_for_path(self, appimage_path):
        appimage_name = os.path.basename(appimage_path)
        
        if self.desktop_entries_dir.exists():
            for desktop_file in self.desktop_entries_dir.glob("*.desktop"):
                try:
                    content = desktop_file.read_text()
                    exec_match = re.search(r'^Exec\s*=\s*(.+)$', content, re.MULTILINE)
                    if exec_match:
                        exec_path = exec_match.group(1).split()[0]
                        if appimage_name.lower() in exec_path.lower():
                            return str(desktop_file)
                except:
                    continue
        
        return None
    
    def on_uninstall_select(self, event):
        selection = self.uninstall_listbox.curselection()
        if selection:
            idx = selection[0]
            if idx < len(self.installed_apps):
                app = self.installed_apps[idx]
                self.selected_info.config(
                    text=f"Path: {app['path']}"
                )
    
    def start_uninstall(self):
        selection = self.uninstall_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Select an AppImage to uninstall!")
            return
        
        idx = selection[0]
        if idx >= len(self.installed_apps):
            return
        
        app = self.installed_apps[idx]
        
        confirm = messagebox.askyesno(
            "Confirm Uninstall",
            f"Uninstall '{app['name']}'?\n\nThis will remove:\n• AppImage file\n• Desktop entry\n• Associated icons"
        )
        
        if confirm:
            self.uninstall_appimage(app)
    
    def uninstall_appimage(self, app):
        try:
            app_name = app['name']
            app_path = app['path']
            
            self.status_text.set(f"Uninstalling {app_name}...")
            
            if os.path.exists(app_path):
                os.remove(app_path)
                self.log(f"Removed: {app_path}")
            
            desktop_removed = False
            if self.desktop_entries_dir.exists():
                for desktop_file in self.desktop_entries_dir.glob("*.desktop"):
                    try:
                        content = desktop_file.read_text()
                        exec_match = re.search(r'^Exec\s*=\s*(.+)$', content, re.MULTILINE)
                        if exec_match:
                            exec_path = exec_match.group(1).split()[0]
                            if app_name.lower() in exec_path.lower():
                                os.remove(desktop_file)
                                self.log(f"Removed desktop: {desktop_file}")
                                desktop_removed = True
                                break
                    except Exception as e:
                        self.log(f"Error: {e}", False)
            
            if not desktop_removed:
                self.log("No desktop entry found")
            
            self.remove_associated_icons(app_name)
            self.update_desktop_database()
            
            self.status_text.set("Done!")
            self.log("✓ Uninstall complete!")
            
            messagebox.showinfo("Success", f"'{app_name}' uninstalled!")
            self.load_installed_apps()
            self.selected_info.config(text="")
            
        except Exception as e:
            self.log(f"Error: {e}", False)
            messagebox.showerror("Error", f"Uninstall failed: {e}")
    
    def remove_associated_icons(self, appimage_name):
        base_name = os.path.splitext(appimage_name)[0].lower()
        base_name = re.sub(r'[-_](amd64|i386|arm64|x86_64|AppImage)$', '', base_name, flags=re.IGNORECASE)
        
        removed = []
        for icon_file in self.icons_dir.rglob("*"):
            if icon_file.is_file():
                icon_name = icon_file.stem.lower()
                if base_name in icon_name or icon_name in base_name:
                    try:
                        os.remove(icon_file)
                        removed.append(str(icon_file))
                    except Exception:
                        pass
        
        for r in removed:
            self.log(f"Removed icon: {os.path.basename(r)}")
    
    def log(self, message, success=True):
        self.log_text.config(state=NORMAL)
        color = self.success_color if success else self.error_color
        self.log_text.insert(END, f"{'✓' if success else '✗'} {message}\n", "ok" if success else "err")
        self.log_text.tag_config("ok", foreground=color)
        self.log_text.tag_config("err", foreground=self.error_color)
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)
    
    def browse_appimage(self):
        filename = filedialog.askopenfilename(
            title="Select AppImage",
            filetypes=[("AppImage files", "*.AppImage *.appimage"), ("All files", "*.*")]
        )
        if filename:
            self.selected_appimage.set(filename)
            basename = os.path.basename(filename)
            name_without_ext = os.path.splitext(basename)[0]
            name_clean = re.sub(r'[-_](amd64|i386|arm64|x86_64|AppImage)$', '', name_without_ext, flags=re.IGNORECASE)
            self.app_name.set(name_clean)
            
            if not os.access(filename, os.X_OK):
                if self.make_executable(filename):
                    self.log(f"Made executable: {basename}")
    
    def start_installation(self):
        appimage_path = self.selected_appimage.get().strip()
        
        if not appimage_path:
            messagebox.showerror("Error", "Select an AppImage file!")
            return
        
        if not os.path.exists(appimage_path):
            messagebox.showerror("Error", "File does not exist!")
            return
        
        if not os.access(appimage_path, os.X_OK):
            self.log("Making executable...")
            if not self.make_executable(appimage_path):
                messagebox.showerror("Error", "Cannot make file executable!")
                return
        
        self.progress.pack(pady=8)
        self.progress.start()
        
        thread = Thread(target=self.install_appimage, args=(appimage_path,))
        thread.daemon = True
        thread.start()
    
    def install_appimage(self, appimage_path):
        extracted_dir = None
        try:
            appimage_name = os.path.basename(appimage_path)
            app_name = self.app_name.get().strip() or os.path.splitext(appimage_name)[0]
            
            self.log(f"Installing: {appimage_name}")
            
            self.status_text.set("Extracting...")
            extracted_dir = self.extract_appimage(appimage_path)
            
            if extracted_dir:
                self.log(f"Extracted")
                desktop_file, icon_path = self.find_desktop_and_icon(extracted_dir)
                if desktop_file:
                    self.log(f"Found desktop file")
                if icon_path:
                    self.log(f"Found best icon")
            else:
                self.log("Extraction failed", False)
                desktop_file, icon_path = None, None
            
            self.status_text.set("Copying...")
            dest_appimage = self.applications_dir / appimage_name
            shutil.copy2(appimage_path, dest_appimage)
            self.make_executable(dest_appimage)
            self.log(f"Copied to ~/Applications")
            
            final_icon_path = None
            if icon_path:
                self.status_text.set("Installing icon...")
                final_icon_path = self.install_icon(icon_path, app_name)
            
            self.status_text.set("Creating desktop entry...")
            if desktop_file and extracted_dir:
                self.modify_and_install_desktop(desktop_file, dest_appimage, final_icon_path, app_name)
            else:
                self.create_basic_desktop_entry(dest_appimage, final_icon_path, app_name)
            
            self.status_text.set("Updating database...")
            self.update_desktop_database()
            
            self.status_text.set("Done!")
            self.log("✓ Installation complete!", True)
            
            messagebox.showinfo("Success", f"'{app_name}' installed!")
            
        except Exception as e:
            self.log(f"Error: {e}", False)
            messagebox.showerror("Error", f"Install failed: {e}")
            self.status_text.set("Failed!")
        
        finally:
            self.cleanup_temp(extracted_dir)
            self.progress.stop()
            self.progress.pack_forget()
    
    def cleanup_temp(self, extracted_dir):
        try:
            if extracted_dir and os.path.exists(extracted_dir):
                temp_parent = os.path.dirname(extracted_dir)
                if 'geardevil' in temp_parent or 'tmp' in temp_parent.lower():
                    shutil.rmtree(temp_parent, ignore_errors=True)
                    self.log("Cleaned up temp files")
        except Exception:
            pass
    
    def extract_appimage(self, appimage_path):
        try:
            temp_dir = tempfile.mkdtemp(prefix="geardevil_")
            
            result = subprocess.run(
                [appimage_path, "--appimage-extract"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            squashfs_dir = Path(temp_dir) / "squashfs-root"
            if squashfs_dir.exists():
                return str(squashfs_dir)
            
            return None
            
        except Exception:
            return None
    
    def find_desktop_and_icon(self, extracted_dir):
        desktop_file = None
        icon_path = None
        best_icon_size = 0
        
        for root, dirs, files in os.walk(extracted_dir):
            for f in files:
                if f.endswith('.desktop'):
                    desktop_file = os.path.join(root, f)
                    break
            if desktop_file:
                break
        
        icon_extensions = ['.png', '.svg', '.xpm', '.ico']
        icon_search_paths = [
            os.path.join(extracted_dir, "usr", "share", "icons"),
            os.path.join(extracted_dir, "usr", "share", "pixmaps"),
            os.path.join(extracted_dir, "icons"),
            extracted_dir,
        ]
        
        all_icons = []
        
        for search_path in icon_search_paths:
            if not os.path.exists(search_path):
                continue
            
            for root, dirs, files in os.walk(search_path):
                for f in files:
                    if any(f.endswith(ext) for ext in icon_extensions):
                        full_path = os.path.join(root, f)
                        size = self.parse_icon_size(root, full_path)
                        all_icons.append((full_path, size))
        
        if all_icons:
            all_icons.sort(key=lambda x: x[1], reverse=True)
            icon_path, best_icon_size = all_icons[0]
        
        return desktop_file, icon_path
    
    def parse_icon_size(self, folder_path, icon_path):
        folder_name = os.path.basename(folder_path)
        if 'x' in folder_name:
            parts = folder_name.split('x')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                return int(parts[0])
        
        parent = os.path.dirname(folder_path)
        parent_name = os.path.basename(parent)
        if 'x' in parent_name:
            parts = parent_name.split('x')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                return int(parts[0])
        
        if icon_path.endswith('.svg'):
            return 1000
        
        if icon_path.endswith('.png'):
            try:
                with open(icon_path, 'rb') as f:
                    f.read(24)
                    import struct
                    data = f.read(4)
                    if data == b'IHDR':
                        width, height = struct.unpack('>II', f.read(8))
                        return max(width, height)
            except:
                pass
        
        return 16
    
    def install_icon(self, icon_path, app_name):
        try:
            _, ext = os.path.splitext(icon_path)
            safe_name = re.sub(r'[^\w\-.]', '_', app_name)
            
            actual_size = self.parse_icon_size("", icon_path)
            
            if actual_size >= 256:
                icon_dir = self.icons_dir / "hicolor" / "256x256" / "apps"
            elif actual_size >= 128:
                icon_dir = self.icons_dir / "hicolor" / "128x128" / "apps"
            elif actual_size >= 64:
                icon_dir = self.icons_dir / "hicolor" / "64x64" / "apps"
            elif actual_size >= 48:
                icon_dir = self.icons_dir / "hicolor" / "48x48" / "apps"
            else:
                icon_dir = self.icons_dir / "hicolor" / "256x256" / "apps"
            
            icon_dir.mkdir(parents=True, exist_ok=True)
            
            dest_icon = icon_dir / f"{safe_name}{ext}"
            shutil.copy2(icon_path, dest_icon)
            
            return str(dest_icon)
            
        except Exception as e:
            self.log(f"Icon error: {e}", False)
            return None
    
    def modify_and_install_desktop(self, desktop_file, appimage_path, icon_path, app_name):
        try:
            with open(desktop_file, 'r') as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                stripped = line.strip()
                
                if stripped.startswith('Exec='):
                    parts = stripped.split(None, 1)
                    args = parts[1] if len(parts) > 1 else '%U'
                    new_lines.append(f'Exec={appimage_path} {args}\n')
                elif stripped.startswith('Icon=') and icon_path:
                    new_lines.append(f'Icon={icon_path}\n')
                else:
                    new_lines.append(line)
            
            content = ''.join(new_lines)
            
            if 'Terminal=' not in content:
                content += '\nTerminal=false\n'
            
            if 'Type=Application' not in content:
                content += 'Type=Application\n'
            
            safe_name = re.sub(r'[^\w\-.]', '_', app_name)
            desktop_filename = f"{safe_name}.desktop"
            dest_desktop = self.desktop_entries_dir / desktop_filename
            
            with open(dest_desktop, 'w') as f:
                f.write(content)
            
            os.chmod(dest_desktop, 0o755)
            
            self.log(f"Desktop entry created")
            
        except Exception as e:
            self.log(f"Desktop error: {e}", False)
            self.create_basic_desktop_entry(appimage_path, icon_path, app_name)
    
    def create_basic_desktop_entry(self, appimage_path, icon_path, app_name):
        try:
            safe_name = re.sub(r'[^\w\-.]', '_', app_name)
            desktop_filename = f"{safe_name}.desktop"
            dest_desktop = self.desktop_entries_dir / desktop_filename
            
            content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={app_name}
Exec={appimage_path} %U
Terminal=false
Categories=Utility;
"""
            if icon_path:
                content += f"Icon={icon_path}\n"
            
            with open(dest_desktop, 'w') as f:
                f.write(content)
            
            os.chmod(dest_desktop, 0o755)
            
            self.log(f"Basic desktop entry created")
            
        except Exception as e:
            self.log(f"Error: {e}", False)
    
    def update_desktop_database(self):
        try:
            subprocess.run(
                ['update-desktop-database', str(self.desktop_entries_dir)],
                capture_output=True,
                timeout=30
            )
            
            try:
                subprocess.run(
                    ['gtk-update-icon-cache', '-f', '-t', str(self.icons_dir)],
                    capture_output=True,
                    timeout=30
                )
            except:
                pass
            
            self.log("Database updated")
            
        except Exception as e:
            self.log(f"Database warning: {e}", False)


def main():
    root = Tk()
    
    try:
        style = ttk.Style()
        style.theme_use('clam')
    except:
        pass
    
    app = GearDevil(root)
    root.mainloop()


if __name__ == "__main__":
    main()