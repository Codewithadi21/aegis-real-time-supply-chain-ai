"""Optional Beam DirectRunner demonstration that does not use cloud resources."""
import json
import apache_beam as beam
from aegis.events import new_sale
from scripts.beam_pipeline import Validate


def run():
    good=json.dumps(new_sale()).encode()
    bad=b'{invalid json'
    with beam.Pipeline() as p:
        out=(p | beam.Create([good,bad]) | beam.ParDo(Validate()).with_outputs('rejected',main='valid'))
        out.valid | 'PrintValid' >> beam.Map(lambda x:print('VALID',x['event_id']))
        out.rejected | 'PrintRejected' >> beam.Map(lambda x:print('REJECTED',x['error_reason']))

if __name__=='__main__':run()
