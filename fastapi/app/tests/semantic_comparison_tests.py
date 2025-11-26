from app.ai.semantic_comparison import semantic_compare
from tqdm import tqdm

testset = {
    "complete_text": [
        "The Eiffel Tower was completed in 1889. Stands 330 meters tall, and was designed by Gustave Eiffel for the World's Fair.",
        "The iPhone 15 Pro features a titanium frame, weighs 187 grams, and includes a 48-megapixel main camera.",
        "Lake Baikal in Russia is the world's deepest lake at 1,642 meters, contains 23% of the world's fresh surface water, and is approximately 25 million years old.",
        "Tesla was founded in 2003, is headquartered in Austin, Texas, and employs over 140,000 people worldwide.",
        "Mars has two moons named Phobos and Deimos, completes one orbit around the Sun in 687 Earth days, and has a diameter of 6,779 kilometers.",
        "\"1984\" was published in 1949, written by George Orwell, and takes place in a dystopian totalitarian society.",
        "Usain Bolt set the 100-meter world record at 9.58 seconds in Berlin during the 2009 World Championships.",
        "Gold has the atomic number 79, a melting point of 1,064 degrees Celsius, and is represented by the symbol Au."
        "Python was created by Guido van Rossum, first released in 1991, and is known for its emphasis on code readability.",
        "The blue whale is the largest animal on Earth, can reach lengths of 30 meters, and feeds primarily on krill."
    ],
    "incomplete_text": [
        "The Eiffel Tower stands 330 meters tall and was designed by Gustave Eiffel for the World's Fair.",
        "The iPhone 15 Pro features a titanium frame and weighs 187 grams.",
        "Lake Baikal in Russia is the world's deepest lake and is approximately 25 million years old.",
        "Tesla is headquartered in Austin, Texas, and employs over 140,000 people worldwide.",
        "Mars has two moons named Phobos and Deimos and has a diameter of 6,779 kilometers.",
        "\"1984\" was written by George Orwell and takes place in a dystopian totalitarian society.",
        "Usain Bolt set the 100-meter world record at 9.58 seconds in Berlin.",
        "Gold has the atomic number 79 and is represented by the symbol Au.",
        "Python was created by Guido van Rossum and is known for its emphasis on code readability.",
        "The blue whale is the largest animal on Earth and can reach lengths of 30 meters."
    ]
}

def run_semantic_compare_tests():
    complete = testset["complete_text"]
    incomplete = testset["incomplete_text"]

    results = []

    for sample in tqdm(range(len(complete))):
        sample_a = complete[sample]
        sample_b = incomplete[sample]

        result = semantic_compare(sample_a, sample_b, "en", "en", 0.5, "sentence-transformers/LaBSE")
        results.append(result)
    
    return results

test_results = run_semantic_compare_tests()

print(test_results[0])