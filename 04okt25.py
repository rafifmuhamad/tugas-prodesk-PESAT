from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
import os
from PIL import Image as PILImage

class SimpleImageConverter(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=12, padding=18, **kwargs)
        self.selected_path = None
        self.choose_btn = Button(text='Pilih File JPG', font_size=18, size_hint=(1, None), height=50)
        self.choose_btn.bind(on_press=self.open_file_popup)
        self.add_widget(self.choose_btn)
        self.resize_input = TextInput(hint_text='Ukuran baru (misal: 600x400)', multiline=False, size_hint=(1, None), height=40)
        self.add_widget(self.resize_input)
        self.convert_btn = Button(text='Resize & Convert ke PNG', font_size=18, size_hint=(1, None), height=50)
        self.convert_btn.bind(on_press=self.convert_image)
        self.add_widget(self.convert_btn)
        self.result_label = Label(text='', font_size=16, size_hint=(1, None), height=40)
        self.add_widget(self.result_label)
        self.img_preview = Image(size_hint=(1, 0.7), allow_stretch=True, keep_ratio=True)
        self.add_widget(self.img_preview)

    def open_file_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=8, padding=8)
        filechooser = FileChooserListView(filters=['*.jpg', '*.jpeg'], size_hint=(1, 0.9))
        select_btn = Button(text='Pilih', size_hint=(1, 0.1))
        popup = Popup(title='Pilih File Gambar', content=content, size_hint=(0.8, 0.8))
        content.add_widget(filechooser)
        content.add_widget(select_btn)
        def select_file(btn):
            if filechooser.selection:
                self.selected_path = filechooser.selection[0]
                self.choose_btn.text = os.path.basename(self.selected_path)
                popup.dismiss()
        select_btn.bind(on_press=select_file)
        popup.open()

    def convert_image(self, instance):
        if not self.selected_path:
            self.result_label.text = 'Pilih file gambar terlebih dahulu.'
            return
        img_path = self.selected_path
        size_str = self.resize_input.text.strip()
        try:
            w, h = map(int, size_str.lower().replace(' ', '').split('x'))
        except Exception:
            self.result_label.text = 'Format ukuran salah. Contoh: 600x400'
            return
        try:
            pil_img = PILImage.open(img_path)
            pil_img = pil_img.resize((w, h))
            png_path = os.path.splitext(img_path)[0] + '_converted.png'
            pil_img.save(png_path, format='PNG')
            self.result_label.text = f'Gambar berhasil diresize dan dikonversi ke {png_path}'
            self.img_preview.source = png_path
            self.img_preview.reload()
        except Exception as e:
            self.result_label.text = f'Gagal: {e}'

class SimpleImageConverterApp(App):
    def build(self):
        return SimpleImageConverter()

if __name__ == '__main__':
    SimpleImageConverterApp().run()