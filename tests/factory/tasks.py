from faker import Faker

fake = Faker()


def create_fake_task():
    title = fake.sentence(nb_words=6, variable_nb_words=True)
    description = fake.paragraph(nb_sentences=3, variable_nb_sentences=True)
    return {
        "title": title,
        "description": description,
    }
