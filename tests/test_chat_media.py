"""Chat attachment extraction and owned-file retention; no external requests."""
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import chat_media

class ChatMediaTests(unittest.TestCase):
 def test_images_only_and_structured_urls_are_kept(self):
  item={'content':[{'type':'localImage','path':'/home/test/a.png'},{'type':'image','url':'data:image/png;base64,AA=='},{'type':'image_url','image_url':{'url':'https://example.com/a.jpg'}}]}
  with patch.object(chat_media,'image_preview',return_value='preview'):
   media=chat_media.attachments(item)
  self.assertEqual(len(media),3);self.assertTrue(all(x['preview']=='preview' for x in media))
 def test_assistant_markdown_and_generic_files_are_found(self):
  item={'text':'![Рисунок](sandbox:/home/test/art.png)\n[Отчёт](sandbox:/home/test/report.pdf)'}
  with patch.object(chat_media,'image_preview',return_value=''):
   media=chat_media.attachments(item)
  self.assertEqual([m['kind'] for m in media],['image','file'])
  self.assertEqual(media[0]['name'],'Рисунок');self.assertFalse(media[0]['available'])
 def test_remote_images_are_not_downloaded_and_bad_data_is_rejected(self):
  self.assertEqual(chat_media.image_preview('https://example.com/private.png'),'')
  self.assertEqual(chat_media.image_preview('data:text/html;base64,AA=='),'')
  self.assertEqual(chat_media.image_preview('data:image/png;base64,invalid'),'')
 def test_files_outside_home_and_escaping_symlinks_are_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   home=Path(d)/'home';home.mkdir();outside=Path(d)/'private.png';outside.write_bytes(b'not-image')
   (home/'link.png').symlink_to(outside)
   with patch.object(Path,'home',return_value=home):
    self.assertRaises(ValueError,chat_media.local_path,str(outside))
    self.assertRaises(ValueError,chat_media.local_path,str(home/'link.png'))
 def test_owned_copy_survives_original_deletion_and_is_deduplicated(self):
  with tempfile.TemporaryDirectory() as d:
   home=Path(d);source=home/'temporary.png';source.write_bytes(b'test-fixture')
   with patch.object(Path,'home',return_value=home):
    target=chat_media.archive_image(source,home/'state')
    self.assertEqual(chat_media.archive_image(source,home/'state'),target)
   source.unlink();self.assertEqual(target.read_bytes(),b'test-fixture')
 def test_duplicate_references_do_not_duplicate_thumbnails(self):
  item={'content':[{'type':'localImage','path':'/home/test/a.png'}],'text':'![image](sandbox:/home/test/a.png)'}
  self.assertEqual(len(chat_media.references(item)),1)

 def test_image_markup_is_replaced_by_preview_without_exposing_long_paths(self):
  self.assertEqual(chat_media.display_text('Готово\n![Картинка](sandbox:/home/test/image.png)'),'Готово')
  self.assertEqual(chat_media.display_text('[Открыть](https://example.com)'),'[Открыть](https://example.com)')

 def test_owned_image_hash_is_not_exposed_as_a_long_title(self):
  with patch.object(chat_media,'image_preview',return_value='preview'):
   media=chat_media.attachments({'images':['/home/test/'+('a'*64)+'.png']})
  self.assertEqual(media[0]['name'],'Изображение')
