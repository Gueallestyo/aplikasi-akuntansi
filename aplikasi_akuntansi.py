import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

conn = sqlite3.connect('akuntansi.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS barang (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kode TEXT,
    nama TEXT,
    harga_beli REAL,
    harga_jual REAL,
    stok INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS penjualan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tanggal TEXT,
    kode_barang TEXT,
    nama_barang TEXT,
    jumlah INTEGER,
    total REAL
)
''')

conn.commit()

root = tk.Tk()
root.title("Aplikasi Akuntansi - Penjualan & Stok")
root.geometry("800x600")

def refresh_barang_tree():
    for row in barang_tree.get_children():
        barang_tree.delete(row)
    cursor.execute("SELECT * FROM barang")
    for row in cursor.fetchall():
        barang_tree.insert('', 'end', values=row)

def tambah_barang():
    kode = kode_entry.get()
    nama = nama_entry.get()
    harga_beli = float(harga_beli_entry.get())
    harga_jual = float(harga_jual_entry.get())
    stok = int(stok_entry.get())
    cursor.execute("INSERT INTO barang (kode, nama, harga_beli, harga_jual, stok) VALUES (?, ?, ?, ?, ?)",
                   (kode, nama, harga_beli, harga_jual, stok))
    conn.commit()
    refresh_barang_tree()
    messagebox.showinfo("Sukses", "Barang berhasil ditambahkan")

    kode_entry.delete(0, tk.END)
    nama_entry.delete(0, tk.END)
    harga_beli_entry.delete(0, tk.END)
    harga_jual_entry.delete(0, tk.END)
    stok_entry.delete(0, tk.END)

def tambah_penjualan():
    kode = kode_jual_entry.get()
    jumlah = int(jumlah_entry.get())
    cursor.execute("SELECT nama, harga_jual, stok FROM barang WHERE kode = ?", (kode,))
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
    cursor.execute("INSERT INTO penjualan (tanggal, kode_barang, nama_barang, jumlah, total) VALUES (?, ?, ?, ?, ?)",
                   (tanggal, kode, nama_barang, jumlah, total))
    cursor.execute("UPDATE barang SET stok = stok - ? WHERE kode = ?", (jumlah, kode))
    conn.commit()
    messagebox.showinfo("Sukses", "Transaksi berhasil")
    kode_jual_entry.delete(0, tk.END)
    jumlah_entry.delete(0, tk.END)
    refresh_barang_tree()
    refresh_penjualan_tree()

def refresh_penjualan_tree():
    for row in penjualan_tree.get_children():
        penjualan_tree.delete(row)
    cursor.execute("SELECT * FROM penjualan")
    for row in cursor.fetchall():
        penjualan_tree.insert('', 'end', values=row)

frame_barang = tk.LabelFrame(root, text="Manajemen Barang", padx=10, pady=10)
frame_barang.pack(fill="x")

kode_entry = tk.Entry(frame_barang)
kode_entry.grid(row=0, column=1)
kode_label = tk.Label(frame_barang, text="Kode")
kode_label.grid(row=0, column=0)

nama_entry = tk.Entry(frame_barang)
nama_entry.grid(row=0, column=3)
nama_label = tk.Label(frame_barang, text="Nama")
nama_label.grid(row=0, column=2)

harga_beli_entry = tk.Entry(frame_barang)
harga_beli_entry.grid(row=1, column=1)
harga_beli_label = tk.Label(frame_barang, text="Harga Beli")
harga_beli_label.grid(row=1, column=0)

harga_jual_entry = tk.Entry(frame_barang)
harga_jual_entry.grid(row=1, column=3)
harga_jual_label = tk.Label(frame_barang, text="Harga Jual")
harga_jual_label.grid(row=1, column=2)

stok_entry = tk.Entry(frame_barang)
stok_entry.grid(row=2, column=1)
stok_label = tk.Label(frame_barang, text="Stok")
stok_label.grid(row=2, column=0)

tambah_btn = tk.Button(frame_barang, text="Tambah Barang", command=tambah_barang)
tambah_btn.grid(row=2, column=3)

barang_tree = ttk.Treeview(root, columns=("ID", "Kode", "Nama", "Harga Beli", "Harga Jual", "Stok"), show='headings')
barang_tree.heading("ID", text="ID")
barang_tree.heading("Kode", text="Kode")
barang_tree.heading("Nama", text="Nama")
barang_tree.heading("Harga Beli", text="Harga Beli")
barang_tree.heading("Harga Jual", text="Harga Jual")
barang_tree.heading("Stok", text="Stok")
barang_tree.pack(fill="x")

frame_jual = tk.LabelFrame(root, text="Transaksi Penjualan", padx=10, pady=10)
frame_jual.pack(fill="x")

kode_jual_entry = tk.Entry(frame_jual)
kode_jual_entry.grid(row=0, column=1)
kode_jual_label = tk.Label(frame_jual, text="Kode Barang")
kode_jual_label.grid(row=0, column=0)

jumlah_entry = tk.Entry(frame_jual)
jumlah_entry.grid(row=0, column=3)
jumlah_label = tk.Label(frame_jual, text="Jumlah")
jumlah_label.grid(row=0, column=2)

jual_btn = tk.Button(frame_jual, text="Proses Penjualan", command=tambah_penjualan)
jual_btn.grid(row=0, column=4)

penjualan_tree = ttk.Treeview(root, columns=("ID", "Tanggal", "Kode Barang", "Nama Barang", "Jumlah", "Total"), show='headings')
penjualan_tree.heading("ID", text="ID")
penjualan_tree.heading("Tanggal", text="Tanggal")
penjualan_tree.heading("Kode Barang", text="Kode Barang")
penjualan_tree.heading("Nama Barang", text="Nama Barang")
penjualan_tree.heading("Jumlah", text="Jumlah")
penjualan_tree.heading("Total", text="Total")
penjualan_tree.pack(fill="x")

refresh_barang_tree()
refresh_penjualan_tree()

root.mainloop()