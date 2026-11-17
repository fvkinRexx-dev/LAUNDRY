from datetime import datetime, timedelta
from pathlib import Path

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput


# =========================================================
# CLEANWASH LAUNDRY - VERSI KIVY
# Alur: 1. Data Pelanggan -> 2. Pilih Barang -> 3. Pembayaran
# Tema warna pink, seluruh fitur utama Tkinter dipertahankan.
# =========================================================

PINK_TUA = (143 / 255, 73 / 255, 104 / 255, 1)
PINK = (217 / 255, 130 / 255, 165 / 255, 1)
PINK_MUDA = (244 / 255, 198 / 255, 215 / 255, 1)
LATAR = (1, 241 / 255, 245 / 255, 1)
PUTIH = (1, 1, 1, 1)
TEKS = (73 / 255, 53 / 255, 65 / 255, 1)
ABU = (166 / 255, 139 / 255, 152 / 255, 1)
HIJAU = (22 / 255, 134 / 255, 92 / 255, 1)

harga_barang = {
    "Baju": 5000,
    "Celana": 6000,
    "Jaket": 12000,
    "Selimut": 15000,
    "Sprei": 10000,
    "Bedcover": 20000,
}

pengali_layanan = {
    "Cuci Kering": 1.0,
    "Cuci Setrika": 1.4,
    "Setrika Saja": 0.8,
}

DURASI = ["Reguler (3 Hari)", "Express (1 Hari)"]


def rupiah(angka):
    return "Rp " + format(angka, ",.0f").replace(",", ".")


def label(teks="", ukuran=14, warna=TEKS, tinggi=None, bold=False,
          halign="left"):
    w = Label(
        text=str(teks),
        font_size=sp(ukuran),
        color=warna,
        bold=bold,
        halign=halign,
        valign="middle",
        size_hint_y=None,
        height=dp(tinggi or max(30, ukuran * 2)),
    )
    w.bind(size=lambda obj, size: setattr(obj, "text_size", (size[0], None)))
    return w


def tombol(teks, aksi, warna=PINK, tinggi=46):
    b = Button(
        text=teks,
        size_hint_y=None,
        height=dp(tinggi),
        background_normal="",
        background_down="",
        background_color=warna,
        color=PUTIH,
        font_size=sp(13),
        bold=True,
    )
    b.bind(on_release=aksi)
    return b


def field(hint, multiline=False, input_filter=None, tinggi=46):
    return TextInput(
        hint_text=hint,
        multiline=multiline,
        input_filter=input_filter,
        size_hint_y=None,
        height=dp(tinggi),
        padding=(dp(12), dp(12)),
        font_size=sp(14),
        foreground_color=TEKS,
        hint_text_color=ABU,
        background_color=(1, 249 / 255, 251 / 255, 1),
        cursor_color=PINK_TUA,
    )


class CleanWashApp(App):
    def build(self):
        self.title = "CLEANWASH Laundry"
        Window.size = (420, 820)
        Window.minimum_width = 340
        Window.minimum_height = 600
        Window.clearcolor = LATAR

        self.keranjang = {}
        self.data_pelanggan = {}
        self.transaksi_selesai = False
        self.isi_struk = ""

        self.sm = ScreenManager()
        for nama in ("pelanggan", "barang", "pembayaran"):
            self.sm.add_widget(Screen(name=nama))

        self.buat_halaman_pelanggan()
        self.buat_halaman_barang()
        self.buat_halaman_pembayaran()
        self.sm.current = "pelanggan"
        return self.sm

    # ---------- Komponen tampilan umum ----------
    def halaman_dasar(self, screen_name, nomor, judul, keterangan):
        screen = self.sm.get_screen(screen_name)
        screen.clear_widgets()

        root = BoxLayout(
            orientation="vertical",
            padding=(dp(14), dp(10)),
            spacing=dp(8),
        )

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(92),
            spacing=dp(1),
        )
        header.add_widget(label("CLEANWASH LAUNDRY", 19, PINK_TUA, 30, True))
        header.add_widget(label("CLEAN • FRESH • FAST", 10, PINK_TUA, 20))
        header.add_widget(label(f"TAHAP {nomor} DARI 3", 10, PINK, 20, True))
        header.add_widget(label(judul, 21, PINK_TUA, 32, True))
        header.add_widget(label(keterangan, 11, ABU, 26))
        root.add_widget(header)

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(5))
        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(10),
            padding=(0, dp(4), 0, dp(12)),
        )
        content.bind(minimum_height=content.setter("height"))
        scroll.add_widget(content)
        root.add_widget(scroll)

        footer = label("© 2026 CLEANWASH LAUNDRY", 9, ABU, 22, halign="center")
        root.add_widget(footer)
        screen.add_widget(root)
        return content

    def section_title(self, parent, teks):
        parent.add_widget(label(teks, 14, PINK_TUA, 30, True))

    def info_popup(self, judul, pesan):
        box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
        msg = label(pesan, 13, TEKS, 90)
        box.add_widget(msg)
        pop = Popup(title=judul, content=box, size_hint=(0.88, None),
                    height=dp(230), auto_dismiss=False)
        box.add_widget(tombol("OK", lambda *_: pop.dismiss(), PINK_TUA))
        pop.open()

    def konfirmasi(self, judul, pesan, saat_ya):
        box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))
        box.add_widget(label(pesan, 13, TEKS, 80))
        baris = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        pop = Popup(title=judul, content=box, size_hint=(0.88, None),
                    height=dp(220), auto_dismiss=False)
        baris.add_widget(tombol("BATAL", lambda *_: pop.dismiss(), ABU))
        def lanjut(*_):
            pop.dismiss()
            saat_ya()
        baris.add_widget(tombol("YA", lanjut, PINK_TUA))
        box.add_widget(baris)
        pop.open()

    def hitung_total(self):
        layanan = self.data_pelanggan.get("layanan", "Cuci Kering")
        pengali = pengali_layanan.get(layanan, 1.0)
        subtotal = sum(
            harga_barang[nama] * jumlah * pengali
            for nama, jumlah in self.keranjang.items()
        )
        diskon = subtotal * 0.10 if subtotal >= 50000 else 0
        return subtotal, diskon, subtotal - diskon

    # ---------- Halaman 1: Data Pelanggan ----------
    def buat_halaman_pelanggan(self):
        content = self.halaman_dasar(
            "pelanggan", 1, "Data Pelanggan",
            "Masukkan informasi pelanggan dan pilih layanan."
        )
        self.section_title(content, "Informasi Pelanggan")

        content.add_widget(label("Nama Pelanggan", 12, TEKS, 24, True))
        self.entry_nama = field("Masukkan nama pelanggan")
        content.add_widget(self.entry_nama)

        content.add_widget(label("Nomor HP", 12, TEKS, 24, True))
        self.entry_hp = field("Masukkan nomor HP", input_filter="int")
        content.add_widget(self.entry_hp)

        content.add_widget(label("Jenis Layanan", 12, TEKS, 24, True))
        self.combo_layanan = Spinner(
            text="Pilih jenis layanan",
            values=list(pengali_layanan.keys()),
            size_hint_y=None,
            height=dp(46),
            background_normal="",
            background_color=PINK_MUDA,
            color=TEKS,
        )
        content.add_widget(self.combo_layanan)

        content.add_widget(label("Durasi Pengerjaan", 12, TEKS, 24, True))
        self.combo_durasi = Spinner(
            text="Pilih durasi pengerjaan",
            values=DURASI,
            size_hint_y=None,
            height=dp(46),
            background_normal="",
            background_color=PINK_MUDA,
            color=TEKS,
        )
        content.add_widget(self.combo_durasi)

        content.add_widget(label(
            "Harga mengikuti jenis barang dan layanan yang dipilih.",
            10, ABU, 32
        ))
        content.add_widget(tombol("LANJUT PILIH BARANG  →",
                                  self.simpan_data_pelanggan, PINK_TUA, 50))

    def simpan_data_pelanggan(self, *_):
        nama = self.entry_nama.text.strip()
        hp = self.entry_hp.text.strip()
        layanan = self.combo_layanan.text
        durasi = self.combo_durasi.text

        if not nama or not hp or layanan not in pengali_layanan or durasi not in DURASI:
            self.info_popup(
                "Data belum lengkap",
                "Mohon isi nama, nomor HP, jenis layanan, dan durasi laundry."
            )
            return

        self.data_pelanggan = {
            "nama": nama, "hp": hp, "layanan": layanan, "durasi": durasi
        }
        self.sm.current = "barang"
        self.refresh_barang()

    # ---------- Halaman 2: Pilih Barang ----------
    def buat_halaman_barang(self):
        content = self.halaman_dasar(
            "barang", 2, "Pilih Barang Laundry",
            "Tambahkan jenis dan jumlah barang yang ingin dicuci."
        )
        self.section_title(content, "Tambah Barang")

        self.combo_barang = Spinner(
            text="Pilih jenis barang",
            values=list(harga_barang.keys()),
            size_hint_y=None,
            height=dp(46),
            background_normal="",
            background_color=PINK_MUDA,
            color=TEKS,
        )
        content.add_widget(self.combo_barang)

        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        self.entry_jumlah = field("Jumlah barang", input_filter="int")
        self.entry_jumlah.text = "1"
        row.add_widget(self.entry_jumlah)
        row.add_widget(tombol("+ TAMBAH", self.tambah_barang, PINK_TUA))
        content.add_widget(row)

        nav = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        nav.add_widget(tombol("← KEMBALI", lambda *_: setattr(
            self.sm, "current", "pelanggan"), ABU))
        nav.add_widget(tombol("HAPUS PILIHAN", self.hapus_barang_terakhir, PINK_TUA))
        content.add_widget(nav)

        self.section_title(content, "Keranjang Barang")
        self.list_keranjang = GridLayout(
            cols=1, spacing=dp(6), size_hint_y=None
        )
        self.list_keranjang.bind(minimum_height=self.list_keranjang.setter("height"))
        content.add_widget(self.list_keranjang)

        self.label_ringkasan = label("Belum ada barang yang dipilih", 10, ABU, 28)
        content.add_widget(self.label_ringkasan)
        self.label_subtotal_barang = label("Subtotal: Rp 0", 14, PINK_TUA, 30, True)
        content.add_widget(self.label_subtotal_barang)
        content.add_widget(tombol("NEXT → PEMBAYARAN", self.lanjut_ke_pembayaran,
                                  PINK_TUA, 50))

    def tambah_barang(self, *_):
        nama = self.combo_barang.text
        if nama not in harga_barang:
            self.info_popup("Pilih barang", "Silakan pilih jenis barang terlebih dahulu.")
            return
        try:
            jumlah = int(self.entry_jumlah.text)
        except ValueError:
            self.info_popup("Jumlah tidak valid", "Jumlah harus berupa angka bulat.")
            return
        if jumlah <= 0:
            self.info_popup("Jumlah tidak valid", "Jumlah barang harus lebih dari 0.")
            return

        self.keranjang[nama] = self.keranjang.get(nama, 0) + jumlah
        self.entry_jumlah.text = "1"
        self.combo_barang.text = "Pilih jenis barang"
        self.refresh_barang()

    def hapus_barang_terakhir(self, *_):
        if not self.keranjang:
            self.info_popup("Keranjang kosong", "Belum ada barang untuk dihapus.")
            return
        nama = list(self.keranjang.keys())[-1]
        self.keranjang.pop(nama)
        self.refresh_barang()

    def hapus_barang(self, nama):
        self.keranjang.pop(nama, None)
        self.refresh_barang()

    def refresh_barang(self):
        if not hasattr(self, "list_keranjang"):
            return
        self.list_keranjang.clear_widgets()
        layanan = self.data_pelanggan.get("layanan", "Cuci Kering")
        pengali = pengali_layanan.get(layanan, 1.0)

        for nama, jumlah in self.keranjang.items():
            harga_satuan = harga_barang[nama] * pengali
            baris = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(5))
            info = BoxLayout(orientation="vertical", spacing=dp(1))
            info.add_widget(label(nama, 12, TEKS, 25, True))
            info.add_widget(label(
                f"{jumlah} buah × {rupiah(harga_satuan)} = "
                f"{rupiah(harga_satuan * jumlah)}",
                10, ABU, 24
            ))
            baris.add_widget(info)
            baris.add_widget(tombol("HAPUS", lambda _, n=nama: self.hapus_barang(n),
                                    PINK, 38))
            self.list_keranjang.add_widget(baris)

        subtotal, _, _ = self.hitung_total()
        jumlah_jenis = len(self.keranjang)
        jumlah_buah = sum(self.keranjang.values())
        self.label_ringkasan.text = (
            f"{jumlah_jenis} jenis barang • {jumlah_buah} buah"
            if self.keranjang else "Belum ada barang yang dipilih"
        )
        self.label_subtotal_barang.text = f"Subtotal: {rupiah(subtotal)}"

    def lanjut_ke_pembayaran(self, *_):
        if not self.keranjang:
            self.info_popup("Keranjang kosong",
                            "Tambahkan minimal satu barang terlebih dahulu.")
            return
        self.sm.current = "pembayaran"
        self.tampilkan_ringkasan_pembayaran()

    # ---------- Halaman 3: Pembayaran ----------
    def buat_halaman_pembayaran(self):
        content = self.halaman_dasar(
            "pembayaran", 3, "Pembayaran",
            "Periksa pesanan, masukkan uang, lalu proses transaksi."
        )

        self.section_title(content, "Informasi Pelanggan")
        self.label_info_pelanggan = label("-", 11, TEKS, 85)
        content.add_widget(self.label_info_pelanggan)

        self.section_title(content, "Rincian Barang")
        self.list_ringkasan = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.list_ringkasan.bind(minimum_height=self.list_ringkasan.setter("height"))
        content.add_widget(self.list_ringkasan)

        self.label_subtotal_bayar = label("Subtotal: Rp 0", 12, TEKS, 26)
        self.label_diskon_bayar = label("Diskon: Rp 0", 12, HIJAU, 26)
        self.label_total_bayar = label("TOTAL BAYAR: Rp 0", 16, PINK_TUA, 32, True)
        content.add_widget(self.label_subtotal_bayar)
        content.add_widget(self.label_diskon_bayar)
        content.add_widget(self.label_total_bayar)

        self.section_title(content, "Uang Pembayaran (Rp)")
        self.entry_uang_bayar = field("Contoh: 100000", input_filter="int")
        content.add_widget(self.entry_uang_bayar)

        self.label_status_bayar = label("MENUNGGU PEMBAYARAN", 11, ABU, 28, True)
        content.add_widget(self.label_status_bayar)

        nav = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        nav.add_widget(tombol("← KEMBALI", lambda *_: setattr(
            self.sm, "current", "barang"), ABU))
        nav.add_widget(tombol("PROSES BAYAR", self.proses_pembayaran, PINK_TUA))
        content.add_widget(nav)

        self.section_title(content, "Struk Pembayaran")
        self.area_struk = TextInput(
            text="Struk akan tampil setelah pembayaran berhasil.",
            readonly=True,
            multiline=True,
            size_hint_y=None,
            height=dp(260),
            font_size=sp(10),
            foreground_color=TEKS,
            background_color=(1, 249 / 255, 251 / 255, 1),
        )
        content.add_widget(self.area_struk)
        content.add_widget(tombol("SIMPAN STRUK", self.simpan_struk, PINK))
        content.add_widget(tombol("TRANSAKSI BARU", self.reset_transaksi,
                                  PINK_TUA))

    def tampilkan_ringkasan_pembayaran(self):
        d = self.data_pelanggan
        self.label_info_pelanggan.text = (
            f"Nama: {d.get('nama', '-')}\n"
            f"Nomor HP: {d.get('hp', '-')}\n"
            f"Layanan: {d.get('layanan', '-')}\n"
            f"Durasi: {d.get('durasi', '-')}"
        )

        self.list_ringkasan.clear_widgets()
        pengali = pengali_layanan[d["layanan"]]
        for nama, jumlah in self.keranjang.items():
            harga_satuan = harga_barang[nama] * pengali
            self.list_ringkasan.add_widget(label(
                f"{nama}  |  {jumlah} buah  |  "
                f"{rupiah(harga_satuan)} / satuan  |  "
                f"{rupiah(harga_satuan * jumlah)}",
                10, TEKS, 30
            ))

        subtotal, diskon, total = self.hitung_total()
        self.label_subtotal_bayar.text = f"Subtotal: {rupiah(subtotal)}"
        self.label_diskon_bayar.text = f"Diskon: {rupiah(diskon)}"
        self.label_total_bayar.text = f"TOTAL BAYAR: {rupiah(total)}"

    def proses_pembayaran(self, *_):
        if self.transaksi_selesai:
            self.info_popup("Transaksi selesai",
                            "Transaksi ini sudah berhasil dibayar.")
            return
        try:
            uang = int(self.entry_uang_bayar.text.strip())
        except ValueError:
            self.info_popup("Pembayaran tidak valid",
                            "Masukkan jumlah uang berupa angka.")
            return
        if uang < 0:
            self.info_popup("Pembayaran tidak valid",
                            "Uang pembayaran tidak boleh negatif.")
            return

        subtotal, diskon, total = self.hitung_total()
        if uang < total:
            self.info_popup("Uang kurang",
                            f"Pembayaran masih kurang sebesar {rupiah(total - uang)}.")
            return

        kembalian = uang - total
        lama_hari = 3 if self.data_pelanggan["durasi"] == "Reguler (3 Hari)" else 1
        tanggal_selesai = datetime.now() + timedelta(days=lama_hari)
        pengali = pengali_layanan[self.data_pelanggan["layanan"]]

        rincian = ""
        for nama, jumlah in self.keranjang.items():
            harga_satuan = harga_barang[nama] * pengali
            rincian += (
                f"{nama:<13} x{jumlah:<3} "
                f"{rupiah(harga_satuan):>12} = "
                f"{rupiah(harga_satuan * jumlah)}\n"
            )

        self.isi_struk = f"""
========================================
             CLEANWASH LAUNDRY
========================================
             BUKTI PEMBAYARAN
Tanggal Transaksi: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}

Nama Pelanggan : {self.data_pelanggan['nama']}
Nomor HP       : {self.data_pelanggan['hp']}
Jenis Layanan  : {self.data_pelanggan['layanan']}
Durasi Laundry : {self.data_pelanggan['durasi']}
Estimasi Selesai: {tanggal_selesai.strftime('%d-%m-%Y')}

----------------------------------------
                DAFTAR BARANG
----------------------------------------
{rincian}----------------------------------------
             RINCIAN PEMBAYARAN
----------------------------------------
Harga Awal     : {rupiah(subtotal)}
Diskon         : {rupiah(diskon)}
Total Bayar    : {rupiah(total)}
Uang Bayar     : {rupiah(uang)}
Kembalian      : {rupiah(kembalian)}

========================================
           PEMBAYARAN BERHASIL
       Terima kasih telah berkunjung!
========================================
"""
        self.area_struk.text = self.isi_struk
        self.transaksi_selesai = True
        self.label_status_bayar.text = "TRANSAKSI BERHASIL"
        self.label_status_bayar.color = HIJAU
        self.info_popup(
            "Pembayaran berhasil",
            f"Transaksi berhasil!\nTotal: {rupiah(total)}\n"
            f"Kembalian: {rupiah(kembalian)}"
        )

    # ---------- Simpan struk ----------
    def simpan_struk(self, *_):
        if not self.transaksi_selesai:
            self.info_popup(
                "Struk belum tersedia",
                "Selesaikan pembayaran terlebih dahulu sebelum menyimpan struk."
            )
            return

        chooser = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        chooser.add_widget(label("Pilih folder penyimpanan struk:", 12, TEKS, 28))
        path_input = TextInput(
            text=str(Path.home()),
            multiline=False,
            size_hint_y=None,
            height=dp(42),
            font_size=sp(11),
        )
        chooser.add_widget(path_input)
        nama_input = TextInput(
            text=f"CLEANWASH_Struk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            multiline=False,
            size_hint_y=None,
            height=dp(42),
            font_size=sp(11),
        )
        chooser.add_widget(nama_input)
        chooser.add_widget(label(
            "Masukkan lokasi folder dan nama file .txt.", 10, ABU, 28
        ))
        pop = Popup(title="Simpan Struk CLEANWASH", content=chooser,
                    size_hint=(0.92, None), height=dp(260))
        def simpan(*_):
            folder = Path(path_input.text.strip()).expanduser()
            nama_file = nama_input.text.strip()
            if not nama_file:
                self.info_popup("Nama file kosong", "Masukkan nama file struk.")
                return
            if not nama_file.lower().endswith(".txt"):
                nama_file += ".txt"
            try:
                folder.mkdir(parents=True, exist_ok=True)
                tujuan = folder / nama_file
                tujuan.write_text(self.isi_struk + "\n", encoding="utf-8")
                pop.dismiss()
                self.info_popup("Struk tersimpan", f"Struk berhasil disimpan:\n{tujuan}")
            except OSError as error:
                self.info_popup("Gagal menyimpan", f"Struk tidak dapat disimpan:\n{error}")
        chooser.add_widget(tombol("SIMPAN FILE", simpan, PINK_TUA))
        pop.open()

    # ---------- Transaksi baru ----------
    def reset_transaksi(self, *_):
        self.konfirmasi(
            "Transaksi baru",
            "Mulai transaksi baru? Data transaksi saat ini akan dikosongkan.",
            self._reset_transaksi_sekarang,
        )

    def _reset_transaksi_sekarang(self):
        self.keranjang.clear()
        self.data_pelanggan.clear()
        self.transaksi_selesai = False
        self.isi_struk = ""

        self.entry_nama.text = ""
        self.entry_hp.text = ""
        self.combo_layanan.text = "Pilih jenis layanan"
        self.combo_durasi.text = "Pilih durasi pengerjaan"
        self.combo_barang.text = "Pilih jenis barang"
        self.entry_jumlah.text = "1"
        self.entry_uang_bayar.text = ""

        self.area_struk.text = "Struk akan tampil setelah pembayaran berhasil."
        self.label_status_bayar.text = "MENUNGGU PEMBAYARAN"
        self.label_status_bayar.color = ABU
        self.refresh_barang()
        self.sm.current = "pelanggan"


if __name__ == "__main__":
    CleanWashApp().run()
