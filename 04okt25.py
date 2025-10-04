from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from PIL import Image as PILImage
from io import BytesIO
import os
import matplotlib.pyplot as plt
import numpy as np

class ImageConverterApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.img_widget = Image(size_hint=(1, 0.7))
        self.btn_select = Button(text='Pilih Gambar JPG', size_hint=(1, 0.15))
        self.btn_select.bind(on_press=self.open_filechooser)
        self.btn_convert = Button(text='Resize & Convert ke PNG', size_hint=(1, 0.15))
        self.btn_convert.bind(on_press=self.convert_image)
        self.btn_convert.disabled = True
        self.btn_plot = Button(text='Tampilkan Grafik', size_hint=(1, 0.15))
        self.btn_plot.bind(on_press=self.show_graph)
        self.btn_plot.disabled = True

        self.layout.add_widget(self.img_widget)
        self.layout.add_widget(self.btn_select)
        self.layout.add_widget(self.btn_convert)
        self.layout.add_widget(self.btn_plot)
        self.selected_path = None
        return self.layout

    def open_filechooser(self, instance):
        content = BoxLayout(orientation='vertical')
        # Filter filechooser agar bisa memilih semua file gambar dan file di folder Downloads
        filechooser = FileChooserIconView(filters=['*.jpg', '*.jpeg', '*.JPG', '*.JPEG', '*.png', '*.PNG'], path=os.path.expanduser('~/Downloads'))
        popup = Popup(title='Pilih File Gambar', content=content, size_hint=(0.9, 0.9))
        btn_ok = Button(text='OK', size_hint=(1, 0.1))
        btn_cancel = Button(text='Batal', size_hint=(1, 0.1))

        def select_file(instance):
            if filechooser.selection:
                self.selected_path = filechooser.selection[0]
                self.show_image(self.selected_path)
                self.btn_convert.disabled = False
                popup.dismiss()

        btn_ok.bind(on_press=select_file)
        btn_cancel.bind(on_press=popup.dismiss)
        content.add_widget(filechooser)
        content.add_widget(btn_ok)
        content.add_widget(btn_cancel)
        popup.open()

    def show_image(self, path):
        self.img_widget.source = path
        self.img_widget.reload()
        self.btn_plot.disabled = False  # Aktifkan tombol grafik jika gambar sudah ada

    def convert_image(self, instance):
        if not self.selected_path:
            return

        # Popup untuk input ukuran
        popup_layout = BoxLayout(orientation='vertical', spacing=8, padding=8)
        label = Label(text="Masukkan ukuran resize (px):")
        from kivy.uix.textinput import TextInput
        input_width = TextInput(hint_text="Lebar", input_filter='int', multiline=False)
        input_height = TextInput(hint_text="Tinggi", input_filter='int', multiline=False)
        btn_ok = Button(text="OK", size_hint=(1, 0.3))
        popup_layout.add_widget(label)
        popup_layout.add_widget(input_width)
        popup_layout.add_widget(input_height)
        popup_layout.add_widget(btn_ok)
        popup_resize = Popup(title="Ukuran Resize", content=popup_layout, size_hint=(0.6, 0.5))

        def do_resize(instance):
            try:
                width = int(input_width.text)
                height = int(input_height.text)
                if width <= 0 or height <= 0:
                    raise ValueError
            except Exception:
                popup_resize.title = "Ukuran tidak valid!"
                return
            popup_resize.dismiss()
            with PILImage.open(self.selected_path) as img:
                img = img.convert('RGB')
                img_resized = img.resize((width, height))
                output_path = os.path.splitext(self.selected_path)[0] + f'resized{width}x{height}.png'
                output_path = os.path.splitext(self.selected_path)[0] + f'_resized_{width}x{height}.png'
                img_resized.save(output_path, format='PNG')
            self.show_image(output_path)
            popup_done = Popup(
                title='Sukses',
                content=Label(text=f'Gambar disimpan sebagai:\n{output_path}'),
                size_hint=(0.7, 0.3)
            )
            popup_done.open()

        btn_ok.bind(on_press=do_resize)
        popup_resize.open()

    def show_graph(self, instance):
        if not self.img_widget.source:
            return
        img = PILImage.open(self.img_widget.source).convert('RGB')
        arr = np.array(img)
        # Grafik Bar: Histogram warna
        plt.figure(figsize=(12,4))
        plt.subplot(1,3,1)
        for i, color in enumerate(['r','g','b']):
            plt.hist(arr[:,:,i].flatten(), bins=32, color=color, alpha=0.5, label=color)
        plt.title('Histogram Warna (Bar)')
        plt.xlabel('Intensitas')
        plt.ylabel('Jumlah')
        plt.legend()

        # Grafik Scatter: Sebaran pixel R vs G
        plt.subplot(1,3,2)
        plt.scatter(arr[:,:,0].flatten()[::100], arr[:,:,1].flatten()[::100], alpha=0.3, s=2, c='purple')
        plt.title('Scatter Plot R vs G')
        plt.xlabel('Red') 
        plt.ylabel('Green')

        # Grafik Log: Histogram warna skala log
        plt.subplot(1,3,3)
        for i, color in enumerate(['r','g','b']):
            hist, bins = np.histogram(arr[:,:,i].flatten(), bins=32)
            plt.semilogy(bins[:-1], hist, color=color, alpha=0.7, label=color)
        plt.title('Histogram Logaritmik')
        plt.xlabel('Intensitas')
        plt.ylabel('Log Jumlah')
        plt.legend()

        plt.tight_layout()
        plt.show()

if __name__ == '__main__':
    ImageConverterApp().run()