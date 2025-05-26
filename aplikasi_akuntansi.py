import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import simpledialog
import mysql.connector
from datetime import datetime

db = mysql.connector.connect(
    host="localhost",
    user="root",  
    password="", 
    database="Toko_Aksesoris"
)
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS barang (
    kode VARCHAR(20) PRIMARY KEY,
    nama VARCHAR(100),
    harga_beli DECIMAL(10,2),
    harga_jual DECIMAL(10,2),
    stok INT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS penjualan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tanggal DATE,
    kode_barang VARCHAR(20),
    nama_barang VARCHAR(100),
    jumlah INT,
    total DECIMAL(10,2),
    FOREIGN KEY (kode_barang) REFERENCES barang(kode)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS jurnal_umum (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tanggal DATE,
    keterangan VARCHAR(255),
    akun VARCHAR(100),
    debit DECIMAL(10,2),
    kredit DECIMAL(10,2)
)
""")

#dummy
cursor.execute("SELECT COUNT(*) FROM barang WHERE kode = %s", ("BRG001",))
if cursor.fetchone()[0] == 0:
    sql = "INSERT INTO barang (kode, nama, harga_beli, harga_jual, stok) VALUES (%s, %s, %s, %s, %s)"
    val = ("BRG001", "Casing iPhone 15 Pro Max", 50000, 85000, 100)
    cursor.execute(sql, val)
    db.commit()

root = tk.Tk()
root.title("Aplikasi Akuntansi Toko Aksesoris")
root.geometry("1000x800")

# Create Notebook (Tabbed Interface)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Tab 1: Manajemen Barang
frame_barang = ttk.Frame(notebook)
notebook.add(frame_barang, text="Manajemen Barang")

# Tab 2: Transaksi Penjualan
frame_penjualan = ttk.Frame(notebook)
notebook.add(frame_penjualan, text="Transaksi Penjualan")

# Tab 3: Jurnal Umum
frame_jurnal = ttk.Frame(notebook)
notebook.add(frame_jurnal, text="Jurnal Umum")

# ==============================================
# FUNGSI MANAJEMEN BARANG
# ==============================================
def refresh_barang_tree():
    for row in barang_tree.get_children():
        barang_tree.delete(row)
    cursor.execute("SELECT kode, nama, harga_beli, harga_jual, stok FROM barang")
    for row in cursor.fetchall():
        barang_tree.insert('', 'end', values=row)

def tambah_barang():
    try:
        kode = kode_entry.get()
        nama = nama_entry.get()
        harga_beli = float(harga_beli_entry.get())
        harga_jual = float(harga_jual_entry.get())
        stok = int(stok_entry.get())

        cursor.execute("INSERT INTO barang (kode, nama, harga_beli, harga_jual, stok) VALUES (%s, %s, %s, %s, %s)",
                       (kode, nama, harga_beli, harga_jual, stok))
        
        # Mencatat pembelian barang ke jurnal umum
        tanggal = datetime.now().strftime('%Y-%m-%d')
        keterangan = f"Pembelian stok {nama}"
        
        # Jurnal untuk pembelian barang (debit persediaan, kredit kas)
        cursor.execute("""
            INSERT INTO jurnal_umum (tanggal, keterangan, akun, debit, kredit) 
            VALUES (%s, %s, %s, %s, %s)
        """, (tanggal, keterangan, "Persediaan Barang", harga_beli * stok, 0))
        
        cursor.execute("""
            INSERT INTO jurnal_umum (tanggal, keterangan, akun, debit, kredit) 
            VALUES (%s, %s, %s, %s, %s)
        """, (tanggal, keterangan, "Kas", 0, harga_beli * stok))
        
        db.commit()
        refresh_barang_tree()
        messagebox.showinfo("Sukses", "Barang berhasil ditambahkan dan dicatat di jurnal")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Database error: {err}")
    except ValueError:
        messagebox.showerror("Error", "Pastikan input harga dan stok berupa angka")

    kode_entry.delete(0, tk.END)
    nama_entry.delete(0, tk.END)
    harga_beli_entry.delete(0, tk.END)
    harga_jual_entry.delete(0, tk.END)
    stok_entry.delete(0, tk.END)

def edit_barang():
    selected_item = barang_tree.selection()
    if not selected_item:
        messagebox.showwarning("Peringatan", "Pilih barang yang akan diedit")
        return
    
    item = barang_tree.item(selected_item)
    kode = item['values'][0]
    
    # Ambil data barang dari database
    cursor.execute("SELECT nama, harga_beli, harga_jual, stok FROM barang WHERE kode = %s", (kode,))
    result = cursor.fetchone()
    
    # Dialog untuk mengedit
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Barang")
    
    tk.Label(edit_window, text="Kode:").grid(row=0, column=0, sticky="e")
    tk.Label(edit_window, text=kode).grid(row=0, column=1, sticky="w")
    
    tk.Label(edit_window, text="Nama:").grid(row=1, column=0, sticky="e")
    nama_edit = tk.Entry(edit_window)
    nama_edit.grid(row=1, column=1)
    nama_edit.insert(0, result[0])
    
    tk.Label(edit_window, text="Harga Beli:").grid(row=2, column=0, sticky="e")
    harga_beli_edit = tk.Entry(edit_window)
    harga_beli_edit.grid(row=2, column=1)
    harga_beli_edit.insert(0, result[1])
    
    tk.Label(edit_window, text="Harga Jual:").grid(row=3, column=0, sticky="e")
    harga_jual_edit = tk.Entry(edit_window)
    harga_jual_edit.grid(row=3, column=1)
    harga_jual_edit.insert(0, result[2])
    
    tk.Label(edit_window, text="Stok:").grid(row=4, column=0, sticky="e")
    stok_edit = tk.Entry(edit_window)
    stok_edit.grid(row=4, column=1)
    stok_edit.insert(0, result[3])
    
    def simpan_perubahan():
        try:
            nama = nama_edit.get()
            harga_beli = float(harga_beli_edit.get())
            harga_jual = float(harga_jual_edit.get())
            stok = int(stok_edit.get())
            
            cursor.execute("""
                UPDATE barang 
                SET nama = %s, harga_beli = %s, harga_jual = %s, stok = %s 
                WHERE kode = %s
            """, (nama, harga_beli, harga_jual, stok, kode))
            
            db.commit()
            refresh_barang_tree()
            edit_window.destroy()
            messagebox.showinfo("Sukses", "Data barang berhasil diperbarui")
        except ValueError:
            messagebox.showerror("Error", "Pastikan input harga dan stok berupa angka")
    
    tk.Button(edit_window, text="Simpan", command=simpan_perubahan).grid(row=5, columnspan=2)

def hapus_barang():
    selected_item = barang_tree.selection()
    if not selected_item:
        messagebox.showwarning("Peringatan", "Pilih barang yang akan dihapus")
        return
    
    item = barang_tree.item(selected_item)
    kode = item['values'][0]
    nama = item['values'][1]
    
    if messagebox.askyesno("Konfirmasi", f"Apakah Anda yakin ingin menghapus {nama}?"):
        try:
            cursor.execute("DELETE FROM barang WHERE kode = %s", (kode,))
            db.commit()
            refresh_barang_tree()
            messagebox.showinfo("Sukses", "Barang berhasil dihapus")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")

# GUI Manajemen Barang
input_frame = ttk.LabelFrame(frame_barang, text="Input Data Barang", padding=10)
input_frame.pack(fill="x", padx=10, pady=5)

ttk.Label(input_frame, text="Kode").grid(row=0, column=0, sticky="e", padx=5, pady=5)
kode_entry = ttk.Entry(input_frame)
kode_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(input_frame, text="Nama").grid(row=0, column=2, sticky="e", padx=5, pady=5)
nama_entry = ttk.Entry(input_frame)
nama_entry.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(input_frame, text="Harga Beli").grid(row=1, column=0, sticky="e", padx=5, pady=5)
harga_beli_entry = ttk.Entry(input_frame)
harga_beli_entry.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(input_frame, text="Harga Jual").grid(row=1, column=2, sticky="e", padx=5, pady=5)
harga_jual_entry = ttk.Entry(input_frame)
harga_jual_entry.grid(row=1, column=3, padx=5, pady=5)

ttk.Label(input_frame, text="Stok").grid(row=2, column=0, sticky="e", padx=5, pady=5)
stok_entry = ttk.Entry(input_frame)
stok_entry.grid(row=2, column=1, padx=5, pady=5)

button_frame = ttk.Frame(input_frame)
button_frame.grid(row=2, column=2, columnspan=2, pady=5)

ttk.Button(button_frame, text="Tambah", command=tambah_barang).pack(side="left", padx=5)
ttk.Button(button_frame, text="Edit", command=edit_barang).pack(side="left", padx=5)
ttk.Button(button_frame, text="Hapus", command=hapus_barang).pack(side="left", padx=5)

# Treeview untuk daftar barang
list_frame = ttk.LabelFrame(frame_barang, text="Daftar Barang", padding=10)
list_frame.pack(fill="both", expand=True, padx=10, pady=5)

barang_tree = ttk.Treeview(list_frame, columns=("Kode", "Nama", "Harga Beli", "Harga Jual", "Stok"), show='headings')
barang_tree.heading("Kode", text="Kode")
barang_tree.heading("Nama", text="Nama")
barang_tree.heading("Harga Beli", text="Harga Beli")
barang_tree.heading("Harga Jual", text="Harga Jual")
barang_tree.heading("Stok", text="Stok")

barang_tree.column("Kode", width=100)
barang_tree.column("Nama", width=200)
barang_tree.column("Harga Beli", width=100, anchor="e")
barang_tree.column("Harga Jual", width=100, anchor="e")
barang_tree.column("Stok", width=50, anchor="center")

vsb = ttk.Scrollbar(list_frame, orient="vertical", command=barang_tree.yview)
hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=barang_tree.xview)
barang_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

barang_tree.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")
hsb.grid(row=1, column=0, sticky="ew")

list_frame.grid_rowconfigure(0, weight=1)
list_frame.grid_columnconfigure(0, weight=1)

# ==============================================
# FUNGSI TRANSAKSI PENJUALAN
# ==============================================
def refresh_penjualan_tree():
    for row in penjualan_tree.get_children():
        penjualan_tree.delete(row)
    cursor.execute("SELECT id, tanggal, kode_barang, nama_barang, jumlah, total FROM penjualan ORDER BY tanggal DESC, id DESC")
    for row in cursor.fetchall():
        penjualan_tree.insert('', 'end', values=row)

def cari_barang():
    kode = kode_jual_entry.get()
    if not kode:
        messagebox.showwarning("Peringatan", "Masukkan kode barang")
        return
    
    cursor.execute("SELECT nama, harga_jual, stok FROM barang WHERE kode = %s", (kode,))
    result = cursor.fetchone()
    
    if result:
        nama_barang, harga_jual, stok = result
        info_label.config(text=f"{nama_barang} | Harga: Rp{harga_jual:,} | Stok: {stok}")
        harga_jual_var.set(harga_jual)
        stok_var.set(stok)
        jumlah_entry.focus()
    else:
        messagebox.showerror("Error", "Barang tidak ditemukan")
        info_label.config(text="")
        harga_jual_var.set(0)
        stok_var.set(0)

def hitung_total(*args):
    try:
        jumlah = int(jumlah_var.get())
        harga = float(harga_jual_var.get())
        total = jumlah * harga
        total_var.set(f"Rp{total:,}")
    except:
        total_var.set("Rp0")

def proses_penjualan():
    kode = kode_jual_entry.get()
    try:
        jumlah = int(jumlah_var.get())
    except ValueError:
        messagebox.showerror("Error", "Jumlah harus berupa angka")
        return
    
    if jumlah <= 0:
        messagebox.showerror("Error", "Jumlah harus lebih dari 0")
        return
    
    cursor.execute("SELECT nama, harga_jual, stok FROM barang WHERE kode = %s", (kode,))
    result = cursor.fetchone()
    if not result:
        messagebox.showerror("Error", "Barang tidak ditemukan")
        return

    nama_barang, harga_jual, stok = result
    if jumlah > stok:
        messagebox.showerror("Error", "Stok tidak mencukupi")
        return

    total = harga_jual * jumlah
    tanggal = datetime.now().strftime('%Y-%m-%d')

    try:
        cursor.execute("""
            INSERT INTO penjualan (tanggal, kode_barang, nama_barang, jumlah, total) 
            VALUES (%s, %s, %s, %s, %s)
        """, (tanggal, kode, nama_barang, jumlah, total))
        
        cursor.execute("UPDATE barang SET stok = stok - %s WHERE kode = %s", (jumlah, kode))
        
        # Mencatat penjualan ke jurnal umum
        keterangan = f"Penjualan {nama_barang} ({jumlah} pcs)"
        
        # Jurnal untuk penjualan (debit kas, kredit pendapatan)
        cursor.execute("""
            INSERT INTO jurnal_umum (tanggal, keterangan, akun, debit, kredit) 
            VALUES (%s, %s, %s, %s, %s)
        """, (tanggal, keterangan, "Kas", total, 0))
        
        cursor.execute("""
            INSERT INTO jurnal_umum (tanggal, keterangan, akun, debit, kredit) 
            VALUES (%s, %s, %s, %s, %s)
        """, (tanggal, keterangan, "Pendapatan Penjualan", 0, total))
        
        # Jurnal untuk HPP (debit HPP, kredit persediaan)
        cursor.execute("SELECT harga_beli FROM barang WHERE kode = %s", (kode,))
        harga_beli = cursor.fetchone()[0]
        hpp = harga_beli * jumlah
        
        cursor.execute("""
            INSERT INTO jurnal_umum (tanggal, keterangan, akun, debit, kredit) 
            VALUES (%s, %s, %s, %s, %s)
        """, (tanggal, keterangan, "Harga Pokok Penjualan", hpp, 0))
        
        cursor.execute("""
            INSERT INTO jurnal_umum (tanggal, keterangan, akun, debit, kredit) 
            VALUES (%s, %s, %s, %s, %s)
        """, (tanggal, keterangan, "Persediaan Barang", 0, hpp))
        
        db.commit()
        messagebox.showinfo("Sukses", "Transaksi berhasil dan dicatat di jurnal")
        kode_jual_entry.delete(0, tk.END)
        jumlah_var.set("1")
        info_label.config(text="")
        refresh_barang_tree()
        refresh_penjualan_tree()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Database error: {err}")

# GUI Transaksi Penjualan
transaksi_frame = ttk.LabelFrame(frame_penjualan, text="Input Transaksi", padding=10)
transaksi_frame.pack(fill="x", padx=10, pady=5)

ttk.Label(transaksi_frame, text="Kode Barang").grid(row=0, column=0, sticky="e", padx=5, pady=5)
kode_jual_entry = ttk.Entry(transaksi_frame)
kode_jual_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Button(transaksi_frame, text="Cari", command=cari_barang).grid(row=0, column=2, padx=5, pady=5)

info_label = ttk.Label(transaksi_frame, text="", font=('Arial', 10))
info_label.grid(row=1, column=0, columnspan=3, sticky="w", padx=5, pady=5)

ttk.Label(transaksi_frame, text="Jumlah").grid(row=2, column=0, sticky="e", padx=5, pady=5)
jumlah_var = tk.StringVar(value="1")
jumlah_var.trace("w", hitung_total)
jumlah_entry = ttk.Entry(transaksi_frame, textvariable=jumlah_var)
jumlah_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

harga_jual_var = tk.DoubleVar(value=0)
stok_var = tk.IntVar(value=0)

ttk.Label(transaksi_frame, text="Harga Satuan").grid(row=3, column=0, sticky="e", padx=5, pady=5)
ttk.Label(transaksi_frame, textvariable=harga_jual_var).grid(row=3, column=1, sticky="w", padx=5, pady=5)

ttk.Label(transaksi_frame, text="Total").grid(row=4, column=0, sticky="e", padx=5, pady=5)
total_var = tk.StringVar(value="Rp0")
ttk.Label(transaksi_frame, textvariable=total_var).grid(row=4, column=1, sticky="w", padx=5, pady=5)

ttk.Button(transaksi_frame, text="Proses Penjualan", command=proses_penjualan).grid(row=5, column=0, columnspan=3, pady=10)

# Daftar Transaksi Penjualan
daftar_frame = ttk.LabelFrame(frame_penjualan, text="Daftar Transaksi", padding=10)
daftar_frame.pack(fill="both", expand=True, padx=10, pady=5)

penjualan_tree = ttk.Treeview(daftar_frame, columns=("ID", "Tanggal", "Kode Barang", "Nama Barang", "Jumlah", "Total"), show='headings')
penjualan_tree.heading("ID", text="ID")
penjualan_tree.heading("Tanggal", text="Tanggal")
penjualan_tree.heading("Kode Barang", text="Kode Barang")
penjualan_tree.heading("Nama Barang", text="Nama Barang")
penjualan_tree.heading("Jumlah", text="Jumlah")
penjualan_tree.heading("Total", text="Total")

penjualan_tree.column("ID", width=50, anchor="center")
penjualan_tree.column("Tanggal", width=100)
penjualan_tree.column("Kode Barang", width=100)
penjualan_tree.column("Nama Barang", width=200)
penjualan_tree.column("Jumlah", width=80, anchor="center")
penjualan_tree.column("Total", width=120, anchor="e")

vsb = ttk.Scrollbar(daftar_frame, orient="vertical", command=penjualan_tree.yview)
hsb = ttk.Scrollbar(daftar_frame, orient="horizontal", command=penjualan_tree.xview)
penjualan_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

penjualan_tree.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")
hsb.grid(row=1, column=0, sticky="ew")

daftar_frame.grid_rowconfigure(0, weight=1)
daftar_frame.grid_columnconfigure(0, weight=1)

# ==============================================
# FUNGSI JURNAL UMUM
# ==============================================
def refresh_jurnal_tree():
    for row in jurnal_tree.get_children():
        jurnal_tree.delete(row)
    cursor.execute("SELECT id, tanggal, keterangan, akun, debit, kredit FROM jurnal_umum ORDER BY tanggal DESC, id DESC")
    for row in cursor.fetchall():
        jurnal_tree.insert('', 'end', values=row)

def filter_jurnal():
    tanggal_awal = tanggal_awal_entry.get()
    tanggal_akhir = tanggal_akhir_entry.get()
    
    query = "SELECT id, tanggal, keterangan, akun, debit, kredit FROM jurnal_umum WHERE 1=1"
    params = []
    
    if tanggal_awal:
        query += " AND tanggal >= %s"
        params.append(tanggal_awal)
    if tanggal_akhir:
        query += " AND tanggal <= %s"
        params.append(tanggal_akhir)
    
    query += " ORDER BY tanggal DESC, id DESC"
    
    cursor.execute(query, params)
    
    for row in jurnal_tree.get_children():
        jurnal_tree.delete(row)
    
    for row in cursor.fetchall():
        jurnal_tree.insert('', 'end', values=row)

def tambah_jurnal_manual():
    add_window = tk.Toplevel(root)
    add_window.title("Tambah Jurnal Manual")
    
    ttk.Label(add_window, text="Tanggal (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    tanggal_entry = ttk.Entry(add_window)
    tanggal_entry.grid(row=0, column=1, padx=5, pady=5)
    tanggal_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
    
    ttk.Label(add_window, text="Keterangan:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    keterangan_entry = ttk.Entry(add_window, width=40)
    keterangan_entry.grid(row=1, column=1, padx=5, pady=5)
    
    ttk.Label(add_window, text="Akun:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    akun_entry = ttk.Entry(add_window)
    akun_entry.grid(row=2, column=1, padx=5, pady=5)
    
    ttk.Label(add_window, text="Debit:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
    debit_entry = ttk.Entry(add_window)
    debit_entry.grid(row=3, column=1, padx=5, pady=5)
    
    ttk.Label(add_window, text="Kredit:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
    kredit_entry = ttk.Entry(add_window)
    kredit_entry.grid(row=4, column=1, padx=5, pady=5)
    
    def simpan_jurnal():
        try:
            tanggal = tanggal_entry.get()
            keterangan = keterangan_entry.get()
            akun = akun_entry.get()
            debit = float(debit_entry.get()) if debit_entry.get() else 0
            kredit = float(kredit_entry.get()) if kredit_entry.get() else 0
            
            cursor.execute("""
                INSERT INTO jurnal_umum (tanggal, keterangan, akun, debit, kredit)
                VALUES (%s, %s, %s, %s, %s)
            """, (tanggal, keterangan, akun, debit, kredit))
            
            db.commit()
            add_window.destroy()
            refresh_jurnal_tree()
            messagebox.showinfo("Sukses", "Jurnal berhasil ditambahkan")
        except ValueError:
            messagebox.showerror("Error", "Debit dan kredit harus berupa angka")
    
    ttk.Button(add_window, text="Simpan", command=simpan_jurnal).grid(row=5, columnspan=2, pady=10)

# GUI Jurnal Umum
filter_frame = ttk.LabelFrame(frame_jurnal, text="Filter Jurnal", padding=10)
filter_frame.pack(fill="x", padx=10, pady=5)

ttk.Label(filter_frame, text="Tanggal Awal:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
tanggal_awal_entry = ttk.Entry(filter_frame)
tanggal_awal_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(filter_frame, text="Tanggal Akhir:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
tanggal_akhir_entry = ttk.Entry(filter_frame)
tanggal_akhir_entry.grid(row=0, column=3, padx=5, pady=5)

ttk.Button(filter_frame, text="Filter", command=filter_jurnal).grid(row=0, column=4, padx=5, pady=5)
ttk.Button(filter_frame, text="Reset", command=refresh_jurnal_tree).grid(row=0, column=5, padx=5, pady=5)
ttk.Button(filter_frame, text="Tambah Jurnal Manual", command=tambah_jurnal_manual).grid(row=0, column=6, padx=5, pady=5)

# Daftar Jurnal Umum
jurnal_list_frame = ttk.LabelFrame(frame_jurnal, text="Daftar Jurnal", padding=10)
jurnal_list_frame.pack(fill="both", expand=True, padx=10, pady=5)

jurnal_tree = ttk.Treeview(jurnal_list_frame, columns=("ID", "Tanggal", "Keterangan", "Akun", "Debit", "Kredit"), show='headings')
jurnal_tree.heading("ID", text="ID")
jurnal_tree.heading("Tanggal", text="Tanggal")
jurnal_tree.heading("Keterangan", text="Keterangan")
jurnal_tree.heading("Akun", text="Akun")
jurnal_tree.heading("Debit", text="Debit")
jurnal_tree.heading("Kredit", text="Kredit")

jurnal_tree.column("ID", width=50, anchor="center")
jurnal_tree.column("Tanggal", width=100)
jurnal_tree.column("Keterangan", width=250)
jurnal_tree.column("Akun", width=150)
jurnal_tree.column("Debit", width=100, anchor="e")
jurnal_tree.column("Kredit", width=100, anchor="e")

vsb = ttk.Scrollbar(jurnal_list_frame, orient="vertical", command=jurnal_tree.yview)
hsb = ttk.Scrollbar(jurnal_list_frame, orient="horizontal", command=jurnal_tree.xview)
jurnal_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

jurnal_tree.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")
hsb.grid(row=1, column=0, sticky="ew")

jurnal_list_frame.grid_rowconfigure(0, weight=1)
jurnal_list_frame.grid_columnconfigure(0, weight=1)

# ==============================================
# INISIALISASI DATA AWAL
# ==============================================
refresh_barang_tree()
refresh_penjualan_tree()
refresh_jurnal_tree()

root.mainloop()