from pathlib import Path
import importlib.util,json,unittest
import numpy as np
import pandas as pd
from IPython.core.inputtransformer2 import TransformerManager
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('notebook_support_under_test',ROOT/'src/notebook_support.py')
CHAT=importlib.util.module_from_spec(spec)
spec.loader.exec_module(CHAT)

class WorkflowChecks(unittest.TestCase):
    def test_portable_data_and_document_setup(self):
        import os,tempfile,fitz
        from unittest.mock import patch
        nb=json.loads((ROOT/'notebooks/hospital_supply_chain_chatbot.ipynb').read_text())
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            (base/'data/generated').mkdir(parents=True)
            (base/'corpus').mkdir()
            pd.DataFrame([{'drug_id':'D00001','generic_name':'samplemed','brand_name':'Samplebrand'}]).to_csv(base/'data/generated/drug_master.csv',index=False)
            pd.DataFrame([{'drug_id':'D00001','location_id':'L001','on_hand_qty':3}]).to_csv(base/'data/generated/inventory_lots.csv',index=False)
            pd.DataFrame([{'location_id':'L001'}]).to_csv(base/'data/generated/locations.csv',index=False)
            pd.DataFrame([{'drug_id':'D00001','unit_cost':1.25}]).to_csv(base/'data/generated/cost_contracts.csv',index=False)
            for name in ['orange_book.pdf','ashp_guidelines.pdf']:
                document=fitz.open()
                page=document.new_page()
                page.insert_textbox(fitz.Rect(40,40,550,700),('Synthetic reference passage for a document retrieval software test. No product equivalence is established by this example. '*8),fontsize=10)
                document.save(base/'corpus'/name)
                document.close()
            ns={'display':lambda value:None}
            with patch.dict(os.environ,{'CHATBOT_PROJECT_DIR':str(base)}):
                exec(''.join(nb['cells'][5]['source']),ns)
                cell='\n'.join(line for line in ''.join(nb['cells'][7]['source']).splitlines() if not line.lstrip().startswith('!'))
                exec(cell,ns)
            self.assertGreater(len(ns['corpus_df']),0)
            self.assertTrue(callable(ns['format_mode0_pdf']))
            self.assertEqual(ns['normalize_term_to_ingredients']('Samplebrand')['ingredients'],['samplemed'])

    def test_catalog_and_pdf_helpers(self):
        catalog=pd.DataFrame([{'drug_id':'D00001','generic_name':'samplemed','brand_name':'Samplebrand'}])
        self.assertEqual(CHAT.normalize_catalog_term('Samplebrand stock',catalog)['ingredients'],['samplemed'])
        self.assertEqual(CHAT.normalize_catalog_term('unknown product',catalog)['ingredients'],[])
        self.assertEqual(CHAT.normalize_catalog_term('notsamplemed',catalog)['ingredients'],[])
        hits=pd.DataFrame([{'score':0.5,'doc_id':'TEST','page':2,'chunk_id':'TEST_p2_c0','text':'Synthetic source excerpt.'}])
        self.assertIn('TEST_p2_c0',CHAT.format_mode0_pdf(hits))
        self.assertIn('No matching',CHAT.format_mode0_pdf(hits.assign(score=0)))
        self.assertEqual(CHAT.chunk_text('abcdefghij',6,2),['abcdef','efghij'])
        with self.assertRaises(ValueError):CHAT.chunk_text('abc',3,3)

    def test_operational_paths_from_corrected_cells(self):
        catalog=pd.DataFrame([{'drug_id':'D00001','generic_name':'samplemed','brand_name':'Samplebrand',
                              'strength':'10 mg','dose_form':'tablet','route':'oral','controlled_flag':False,'refrigerated_flag':False}])
        locations=pd.DataFrame([{'location_id':'L001','facility':'Hospital A','area':'Main Pharmacy'}])
        lots=pd.DataFrame([{'drug_id':'D00001','location_id':'L001','on_hand_qty':3,'unit':'tablet',
                           'status':'available','expiration_date':'2030-01-01','lot_number':'LN123456'}])
        contracts=pd.DataFrame([{'drug_id':'D00001','unit_cost':1.25,'vendor':'Synthetic Vendor',
                                'contract_start':'2026-01-01','contract_end':'2030-01-01'}])
        ns={'drug_master':catalog,'locations':locations,'inventory_lots':lots,'cost_contracts':contracts,
            'format_mode0_pdf':CHAT.format_mode0_pdf,
            'normalize_term_to_ingredients':lambda q:CHAT.normalize_catalog_term(q,catalog),
            'retrieve_pdf':lambda q,k:pd.DataFrame([{'score':1.,'doc_id':'TEST','page':1,'chunk_id':'T1','text':'Test excerpt'}])}
        nb=json.loads((ROOT/'notebooks/hospital_supply_chain_chatbot.ipynb').read_text())
        for i in [9,15]:exec(''.join(nb['cells'][i]['source']),ns)
        self.assertIn('D00001',ns['mode0_answer']('How many D00001 at L001?'))
        self.assertIn('Test excerpt',ns['mode0_answer']('reference evidence'))
        self.assertIn('unit_cost',ns['mode1_answer']('cost for D00001'))
        self.assertIn('1.25',ns['mode1_answer']('cost for D00001'))
        alternative=ns['mode1_answer']('Samplebrand substitute')
        self.assertIn('samplemed',alternative)
        self.assertIn('usable_on_hand=3',alternative)

    def test_notebook_syntax(self):
        transform=TransformerManager().transform_cell
        notebook=ROOT/'notebooks/hospital_supply_chain_chatbot.ipynb'
        for cell in json.loads(notebook.read_text())['cells']:
            if cell['cell_type']=='code':
                compile(transform(''.join(cell['source'])),str(notebook),'exec')
                self.assertEqual(cell['outputs'],[])


if __name__=='__main__':unittest.main(verbosity=2)
