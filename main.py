from pathlib import Path
from pytube import YouTube

from textual.app import App, ComposeResult, Screen
from textual.widgets import Button, Header, Footer, Static, Input, Label, ProgressBar
from textual.containers import ScrollableContainer
import pyperclip


async def youtubeDownload(link, progress_callback):
    try:
        path = str(Path.home() / 'Downloads')
        yt = YouTube(link, on_progress_callback=progress_callback)
        yd = yt.streams.get_highest_resolution()
        yd.download(path)
        return yt.title, yt.author
    except Exception as e:
        pass

class Info(Static):
    def compose(self) -> ComposeResult:
        yield Label('Nickname', id='nickname')
        yield Label('Title', id='title')
        yield ProgressBar(total=100, id='progress_bar')


class Download(Static):
    def __init__(self, info_component: Info) -> None:
        super().__init__()
        self.info_component = info_component

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == 'paste':
            clipboard_content = pyperclip.paste()
            input_widget = self.query_one(Input)
            input_widget.value = clipboard_content

        if button_id == 'download':
            input_widget = self.query_one(Input)
            link = input_widget.value

            progress_bar = self.info_component.query_one("#progress_bar", ProgressBar)
            progress_bar.update(progress=0)

            # Call youtubeDownload and get the title and author
            try:
                title, author = await youtubeDownload(link, self.on_progress)

                # Update the labels with the downloaded video's title and author
                label_title = self.info_component.query_one("#title", Label)
                label_title.update(title)
                label_nickname = self.info_component.query_one("#nickname", Label)
                label_nickname.update(author)
            except Exception as e:
                label_title = self.info_component.query_one('#title', Label)
                label_nickname = self.info_component.query_one('#nickname', Label)
                label_title.update('ERROR: WRONG LINK')
                label_nickname.update('ERROR: WRONG LINK')
                pass

    def on_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_of_completion = bytes_downloaded / total_size * 100
        print(f"Total Size: {total_size}, Bytes Downloaded: {bytes_downloaded}, Progress: {percentage_of_completion}")
        progress_bar = self.info_component.query_one("#progress_bar", ProgressBar)
        progress_bar.progress = percentage_of_completion

    def compose(self) -> ComposeResult:
        yield Button("Download", id="download", variant="success")
        yield Button("Paste", id="paste", variant="error")
        yield Input(value='Paste your link here')


class DownloaderApp(App):
    CSS_PATH = "styles.tcss"
    BINDINGS = [('d', 'toggle_dark', 'Toggle Dark Mode'),
                ('v', 'paste', 'Paste From Clipboard'),
                ('c', 'credits', 't.me/kiwashix')
                ]

    def compose(self) -> ComposeResult:
        header = Header()
        footer = Footer()
        info = Info()
        download = Download(info)
        yield header
        yield footer
        yield ScrollableContainer(download, info)

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_paste(self) -> None:
        clipboard_content = pyperclip.paste()
        input_widget = self.query_one(Input)
        input_widget.value = clipboard_content

    def action_second_page(self) -> None:
        self.switch_screen()


if __name__ == '__main__':
    app = DownloaderApp()
    app.run()
