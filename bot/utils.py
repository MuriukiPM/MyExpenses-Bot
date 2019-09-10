import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def convertJson(data):
    facts = list()
    for key, value in data.items():
        if key !='ID' and key !='ChatID':
            facts.append('{} - {}'.format(key, value))

    return ("\n".join(facts).join(['\n', '\n']))