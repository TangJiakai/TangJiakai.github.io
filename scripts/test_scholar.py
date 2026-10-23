import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from update_scholar import parse_metrics, refresh

GOOD='''<div id="gsc_prf_in">Jiakai Tang</div><table id="gsc_rsb_st"><tbody>
<tr><td>Citations</td><td class="gsc_rsb_std">7,207</td><td class="gsc_rsb_std">7198</td></tr>
<tr><td>h-index</td><td class="gsc_rsb_std">15</td><td class="gsc_rsb_std">15</td></tr>
<tr><td>i10-index</td><td class="gsc_rsb_std">16</td><td class="gsc_rsb_std">16</td></tr>
</tbody></table>'''

class ScholarTests(unittest.TestCase):
    def test_all_time_column_and_comma(self):
        self.assertEqual(parse_metrics(GOOD), {'citations':7207,'h_index':15,'i10_index':16})
    def test_wrong_profile_challenge_and_missing_cell(self):
        for bad in [GOOD.replace('Jiakai Tang','Another Person'), '<html>unusual traffic</html>',GOOD.replace('>16<','>—<')]:
            with self.assertRaises(ValueError): parse_metrics(bad)
    def test_failed_fetch_preserves_bytes_and_timestamp(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'scholar.json';old=b'{"updated_at":"original","citations":7207}\n';p.write_bytes(old)
            self.assertFalse(refresh(p,lambda:'<html>CAPTCHA</html>'))
            self.assertEqual(p.read_bytes(),old)
            def blocked(): raise HTTPError('https://scholar.google.com',429,'limited',None,None)
            self.assertFalse(refresh(p,blocked));self.assertEqual(p.read_bytes(),old)
    def test_success_writes_valid_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'scholar.json';self.assertTrue(refresh(p,lambda:GOOD))
            value=json.loads(p.read_text());self.assertEqual(value['i10_index'],16);self.assertIn('updated_at',value)

if __name__=='__main__': unittest.main()
