from data_augmentation.templates import RARE_CLASS_SAMPLES
from data_augmentation.augmenter import augment_text

for label, samples in RARE_CLASS_SAMPLES.items():
    print(f"{label}: 100 samples generated")

    count = 0
    while count < 100:
        for sample in samples:
            print("-", augment_text(sample))
            count += 1
            if count == 100:
                break