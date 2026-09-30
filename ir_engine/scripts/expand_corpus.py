#!/usr/bin/env python3
"""
expand_corpus.py — Expand VaartaVerse Folk Tale Corpus
Adds 28 classic Indian folk tales and epic episodes:
  - Akbar & Birbal (5 tales)
  - Tenali Raman (5 tales)
  - Ramayana (6 tales)
  - Mahabharata (6 tales)
  - Renowned Pan-Indian Folk Tales (6 tales: Panchatantra, Bengali, Kashmiri, Rajasthani)
"""

import json
from pathlib import Path

CORPUS_PATH = Path(__file__).parent.parent / "data" / "corpus" / "tales.json"

NEW_TALES = [
    # -------------------------------------------------------------------------
    # Akbar & Birbal
    # -------------------------------------------------------------------------
    {
        "tale_id": "BIR-015",
        "tale_type": "ATU-920",
        "title": "Birbal and the Stolen Gold Coins — The Growing Sticks",
        "region": "Agra / North India",
        "tradition": "Birbal-Akbar",
        "source_collection": "Mughal Court Folk Tales — Traditional Folklore",
        "translator": "Traditional Retelling",
        "collection_era": "c. 1600 CE",
        "raw_text": (
            "A wealthy merchant in Agra came to Emperor Akbar in tears, reporting that one of his "
            "five domestic servants had stolen a pouch containing one hundred gold mohurs from his bedroom "
            "chest. None of the servants admitted the deed. Akbar assigned Birbal to find the culprit. "
            "Birbal gathered the five suspects in a courtyard and gave each servant a wooden stick of identical "
            "length. He told them: These are enchanted sticks from the forest of sages. The stick belonging "
            "to the true thief will miraculously grow by two inches tonight before the sun rises. Return to me "
            "tomorrow at dawn with your sticks. The innocent servants slept peacefully, knowing they had "
            "committed no crime. But the guilty servant was gripped by terror. He thought: If my stick grows "
            "two inches, my guilt will be exposed. Therefore, I shall cut two inches off right now, and by dawn "
            "it will grow back to the standard size. He carefully trimmed two inches off his stick. Next morning, "
            "Birbal measured all the sticks before Akbar. Four sticks were equal in length, while the thief's "
            "stick was two inches shorter than all the others. The thief fell to his knees and confessed his crime."
        ),
    },
    {
        "tale_id": "BIR-016",
        "tale_type": "ATU-920",
        "title": "The Well and the Water — Birbal's Astute Verdict",
        "region": "Agra / North India",
        "tradition": "Birbal-Akbar",
        "source_collection": "Mughal Court Folk Tales — Traditional Folklore",
        "translator": "Traditional Retelling",
        "collection_era": "c. 1600 CE",
        "raw_text": (
            "A cunning grain merchant sold a stone water well on his land to a humble farmer named Ramdas for thirty "
            "silver rupees. The next morning, when Ramdas came with his leather buckets to draw water to irrigate his "
            "parched fields, the merchant blocked him with a mocking grin. He said: Friend, I sold you the well, but I "
            "never sold you the water inside the well! If you wish to draw a single drop of water, you must pay me five "
            "copper coins each morning. Ramdas, devastated, presented his grievance to Akbar's royal court. The courtiers "
            "scratched their heads, for the deed indeed mentioned only the well. Birbal smiled and addressed the merchant: "
            "You are absolutely correct; the well belongs to the farmer, and the water belongs to you. But tell me, since the "
            "well is the farmer's property, by what authority are you keeping your water stored in his well without paying rent? "
            "You must either remove every drop of your water immediately from the well, or pay the farmer twenty silver coins per "
            "day for storage rent. The greedy merchant was trapped by his own cunning, begged for mercy, and withdrew his fraudulent claim."
        ),
    },
    {
        "tale_id": "BIR-017",
        "tale_type": "ATU-920",
        "title": "The Pot of Wisdom for the King of Persia",
        "region": "Agra / North India",
        "tradition": "Birbal-Akbar",
        "source_collection": "Mughal Court Folk Tales — Traditional Folklore",
        "translator": "Traditional Retelling",
        "collection_era": "c. 1600 CE",
        "raw_text": (
            "The Shah of Persia sent an imperial envoy to Emperor Akbar with a witty diplomatic challenge. The letter stated: "
            "We hear that the court of Hindustan is blessed with boundless wisdom. Our treasury has jewels and gold in plenty, but our "
            "monarch desires a vessel filled with pure wisdom. We pray you send us a clay pot brimming with wisdom. Akbar was vexed "
            "and consulted Birbal. Birbal asked for three weeks' time and a narrow-necked earthen pot. He carried the pot to a pumpkin "
            "patch where a young pumpkin vine had just begun to flower. Birbal carefully guided a tiny green pumpkin through the narrow "
            "neck into the belly of the pot, leaving the stem attached to the plant. Bathed in summer sunshine and rain, the pumpkin grew "
            "so immense that it completely filled the interior of the pot. When it was fully ripe, Birbal severed the vine, sealed the pot "
            "with silk, and presented it to Akbar to dispatch to Persia with a letter: Here is a pot of wisdom. Take out the fruit of wisdom "
            "without breaking the clay pot or cutting the fruit. If you can achieve this, you are truly wise. The Persian king read the "
            "message, inspected the unbroken vessel, and admitted that Akbar's court harbored wisdom beyond compare."
        ),
    },
    {
        "tale_id": "BIR-018",
        "tale_type": "ATU-920",
        "title": "Birbal Paints the Emperor's Imagination",
        "region": "Agra / North India",
        "tradition": "Birbal-Akbar",
        "source_collection": "Mughal Court Folk Tales — Traditional Folklore",
        "translator": "Traditional Retelling",
        "collection_era": "c. 1600 CE",
        "raw_text": (
            "One pleasant evening in the gardens of Fatehpur Sikri, Emperor Akbar was admiring court artists painting detailed portraits "
            "of royal falcons and blossoming gardens. Akbar turned to Birbal and said: You boast of intellect in statecraft, but art is the "
            "true measure of sensitivity. I challenge you to paint a picture within one week that captures action, movement, and the spirit of "
            "life. If you fail, you shall pay fifty gold coins. Birbal accepted with a respectful bow. A week later the court assembled. "
            "Birbal brought in a large wooden easel covered with a velvet shroud. With grand flourish he pulled away the velvet. The courtiers "
            "gasped: the canvas was painted entirely with a patch of lush green grass and blue clouds above, with nothing else on it. Akbar frowned "
            "and demanded: Birbal, is this your masterpiece? What does this represent? Birbal replied: Your Majesty, it represents a sacred cow "
            "eating sweet meadow grass. Akbar asked: But where is the cow? Birbal bowed: Your Majesty, the cow ate all the grass and has walked "
            "away to drink from the Yamuna. You instructed me to capture action and imagination; an intelligent viewer must imagine the departed cow. "
            "Akbar laughed heartily at Birbal's irrepressible wit and rewarded him with a pearl necklace."
        ),
    },
    {
        "tale_id": "BIR-019",
        "tale_type": "ATU-920",
        "title": "The Cold Yamuna and the Washerman's Reward",
        "region": "Agra / North India",
        "tradition": "Birbal-Akbar",
        "source_collection": "Mughal Court Folk Tales — Traditional Folklore",
        "translator": "Traditional Retelling",
        "collection_era": "c. 1600 CE",
        "raw_text": (
            "On a bitter winter night when frost coated the marble terraces of Agra, Emperor Akbar proclaimed that anyone who could stand "
            "neck-deep in the freezing waters of the Yamuna from sunset to sunrise would receive a chest of gold coins and royal land. A poor "
            "washerman named Dinu, desperate to feed his starving family, accepted the ordeal. Through howling icy winds and biting cold, Dinu "
            "stood shivering in the dark river until morning light. When he arrived shivering at court to claim his prize, a jealous courtier "
            "remarked: Your Majesty, as he stood in the water, he kept his gaze fixed upon the burning palace lamp atop the royal tower two miles away. "
            "He took warmth from that flame, and therefore his feat was aided by palace fire! Akbar, swayed by the courtier, denied Dinu the reward. "
            "Next day Birbal did not appear at court. Akbar visited Birbal's garden and found him sitting beside a tall bamboo tripod. A cooking "
            "pot hung twenty feet in the air, while a tiny handful of twigs burned on the ground far below. Akbar asked: Birbal, are you mad? How can "
            "that tiny fire cook the lentils in a pot hanging twenty cubits above it? Birbal replied: Your Majesty, if a palace lamp two miles across "
            "the frozen city could warm a man submerged in icy water, surely this fire can cook my dinner. Akbar recognized his injustice, summoned "
            "the washerman, and bestowed the promised gold upon him."
        ),
    },

    # -------------------------------------------------------------------------
    # Tenali Raman
    # -------------------------------------------------------------------------
    {
        "tale_id": "TEN-012",
        "tale_type": "ATU-920",
        "title": "Tenali Raman and the Greedy Persian Horse Trader",
        "region": "Vijayanagara / South India",
        "tradition": "Tenali Raman",
        "source_collection": "Tales of the Vijayanagara Court — Folk Traditions",
        "translator": "Traditional Retelling",
        "collection_era": "c. 1520 CE",
        "raw_text": (
            "A wealthy Persian horse merchant brought a magnificent herd of Arabian war stallions to the court of King Krishnadevaraya. "
            "The merchant offered to supply hundreds of similar horses if the king would pay upfront for the breeding and maintenance of young "
            "colts. The king entrusted royal courtiers and Tenali Raman each with one young colt and fifty gold coins per month for its feed. "
            "The courtiers spent the money pampering their horses with barley, almond paste, and milk, allowing the horses to grow sleek and heavy. "
            "Tenali Raman, however, built a tiny bamboo stall for his colt and fed it only a single fistful of dry straw through a narrow window "
            "each morning, leaving a bundle of fresh sweet green grass tied just beyond the window out of the horse's reach. Months later the royal "
            "inspection took place. The king's chief examiner, sporting a magnificent beard like a bush of golden straw, approached Tenali's "
            "shed to inspect the colt. As soon as the examiner peeked his head through the window, the starving horse mistook his bushy beard for sweet "
            "hay, clamped its teeth into it, and pulled with all its might. The examiner screamed in agony as the horse refused to let go. Raman came "
            "out and explained: Your Majesty, a war horse must not become a pampered pet fed on sweet almonds; a horse that hungers for action will "
            "conquer any enemy. The court roared with laughter, and the king recognized Raman's satire on the court's wasteful horse contract."
        ),
    },
    {
        "tale_id": "TEN-014",
        "tale_type": "MYT-FOLK",
        "title": "The Boon of Goddess Kali and the Thousand Running Noses",
        "region": "Vijayanagara / South India",
        "tradition": "Tenali Raman",
        "source_collection": "Tales of the Vijayanagara Court — Folk Traditions",
        "translator": "Traditional Retelling",
        "collection_era": "c. 1520 CE",
        "raw_text": (
            "In his youth, Tenali Ramalinga was poor and uneducated. A wandering sadhu took pity on him and taught him a secret invocation to "
            "Goddess Mahakali at the ancient midnight temple on the hill. Raman recited the sacred mantra three million times with unwavering "
            "concentration. At midnight the temple shook, and Goddess Kali appeared in her terrifying cosmic form, bearing a thousand heads with fiery "
            "eyes and twenty arms holding flashing tridents. While any mortal would have fainted in horror, Tenali looked up at the thousand faces "
            "and burst into uncontrollable laughter. Kali was astonished and enraged. She bellowed: Impudent mortal! Gods and demons tremble before "
            "my terrible majesty; why do you mock me? Tenali folded his hands and replied: O Mother of the Universe, forgive this humble servant! "
            "I was merely struck by a thought: humans have only one nose, and when we catch a common winter cold and sniffle, we struggle miserably "
            "to wipe it with two hands. If you catch a cold, Mother, with a thousand noses running all at once and only twenty hands, how on earth do you "
            "manage to wipe them all? Kali, surprised by his audacious wit and utterly devoid of fear, chuckled and granted him a boon: You shall be "
            "celebrated throughout history as a Vikatakavi, a brilliant jester-poet who shall disarm emperors with laughter and wisdom."
        ),
    },
    {
        "tale_id": "TEN-015",
        "tale_type": "ATU-920",
        "title": "Tenali Paints the Other Side of the Horse",
        "region": "Vijayanagara / South India",
        "tradition": "Tenali Raman",
        "source_collection": "Tales of the Vijayanagara Court — Folk Traditions",
        "translator": "Traditional Retelling",
        "collection_era": "c. 1520 CE",
        "raw_text": (
            "A master painter from foreign lands exhibited a detailed landscape painting before King Krishnadevaraya. The king praised the artist "
            "profusely and rewarded him with a bag of gold. Tenali Raman observed the painting and remarked: The painting has merit, but the artist has "
            "failed to show the other side of the palace and the back of the people. How can a painting be called complete when half of every subject "
            "is missing? The king retorted: You ignorant jester, art requires the viewer to imagine what is hidden! If you think painting is so simple, "
            "I give you one month and all the paints you desire. Produce a painting superior to this, or you shall be exiled from Vijayanagara. One month "
            "later, Raman entered the royal assembly carrying a large stretched canvas covered in white silk. When unveiled, the canvas was completely "
            "white, save for four curving black brushstrokes in one corner resembling horse hooves and a few stray hairs of a tail disappearing past the "
            "frame edge. The king grew furious: Raman, is this an insult? Where is the horse? Raman calmly replied: Your Majesty, remember what you "
            "taught me? Art requires imagination! This is a magnificent war horse grazing in a lush pasture. Its body, neck, head, and rider are all on "
            "the other side of the canvas; you need only use your royal imagination to admire its splendour. Krishnadevaraya laughed at his own words "
            "turned against him and rewarded Raman handsomely."
        ),
    },
    {
        "tale_id": "TEN-016",
        "tale_type": "ATU-920",
        "title": "Tenali Raman and the Proud Pundit Vidyasagar",
        "region": "Vijayanagara / South India",
        "tradition": "Tenali Raman",
        "source_collection": "Tales of the Vijayanagara Court — Folk Traditions",
        "translator": "Traditional Retelling",
        "collection_era": "c. 1520 CE",
        "raw_text": (
            "A renowned and arrogant scholar named Vidyasagar, who had defeated learned pundits across Kashmir, Bengal, and Kashi, arrived at "
            "Vijayanagara with a cartload of scholarly certificates. He challenged King Krishnadevaraya's assembly to debate him in Sanskrit grammar, "
            "logic, and philosophy, declaring that if none could match him, the royal pundits must sign a charter acknowledging him as the supreme scholar "
            "of the earth. The royal scholars trembled, for Vidyasagar's erudition was vast. Tenali Raman stepped forward and promised to debate the "
            "pundit next morning. At the debate, Raman entered in scholar's robes carrying a thick bundle wrapped in opulent gold silk and bound tightly "
            "with a coarse twisted rope. Raman placed the bundle before the assembly and announced: I challenge the great Vidyasagar to debate the "
            "profound doctrines expounded in this rare treatise: Thila-Kashta-Mahishi-Bandhana-Bhasya! Vidyasagar was stunned. He racked his encyclopedic "
            "memory, but had never heard of such a scripture in any school of Vedanta or Mimamsa. Terrified of public humiliation, Vidyasagar packed his "
            "carts in the dead of night and fled the capital. Next morning the king inquired about the sacred treatise. Raman untied the silk: inside were "
            "dry sesame stalks (thila-kashta) tied with an ordinary rope used to tether water buffaloes (mahishi-bandhana). The king marvelled at how "
            "ordinary wit disarmed pedantic pride."
        ),
    },
    {
        "tale_id": "TEN-017",
        "tale_type": "ATU-920",
        "title": "Tenali Raman and the Magic Red Peacocks",
        "region": "Vijayanagara / South India",
        "tradition": "Tenali Raman",
        "source_collection": "Tales of the Vijayanagara Court — Folk Traditions",
        "translator": "Traditional Retelling",
        "collection_era": "c. 1520 CE",
        "raw_text": (
            "A merchant arrived from distant southern shores with a pair of radiant red peacocks, their plumage shimmering with brilliant scarlet "
            "and crimson feathers. He claimed they were born in a sacred valley of ruby dust and demanded a thousand gold coins for the pair. King "
            "Krishnadevaraya, captivated by their exotic beauty, paid the merchant and instructed his aviary masters to take special care of them. "
            "Tenali Raman observed the birds closely and noticed a subtle chemical scent lingering near their cages. Tenali dispatched his scouts to "
            "the outskirts of Vijayanagara and discovered a dyer's workshop where an artisan was experimenting with red madder and safflower dyes. "
            "Tenali bought several cages of ordinary white peacocks, had the dyer coat them in waterproof red pigment, and appeared at court with twenty "
            "identical red birds, offering them to the king for half the price. The king was astonished. Raman then whispered to the palace attendants "
            "to turn on the royal water fountain. As rain and mist showered the aviary, the red dye began to streak and wash away into pink puddles, "
            "revealing ordinary white feathers beneath. The fraudulent merchant was arrested, and Raman demonstrated that greed paints falsehood, "
            "but truth withstands the rain."
        ),
    },

    # -------------------------------------------------------------------------
    # Ramayana
    # -------------------------------------------------------------------------
    {
        "tale_id": "RAM-001",
        "tale_type": "EPIC-RAMAYANA",
        "title": "The Golden Deer of Dandakaranya and the Illusion of Maricha",
        "region": "Dandakaranya / Central India",
        "tradition": "Ramayana",
        "source_collection": "Valmiki Ramayana — Aranya Kanda",
        "translator": "Traditional Epic Translation",
        "collection_era": "c. 500 BCE",
        "raw_text": (
            "During the fourteenth year of exile in the deep Panchavati forest of Dandakaranya, the demon Maricha assumed the form of an "
            "enchanting deer at Ravana's command. The deer's coat gleamed like polished molten gold, dappled with silver spots; its hooves were of "
            "black onyx and its antlers sparkled like clusters of sapphires. As it grazed gracefully near the leaf-thatched hermitage, Sita was "
            "enchanted by its divine beauty and begged Rama to capture it as a companion for their return to Ayodhya. Lakshmana warned: Brother, "
            "no deer in the three worlds possesses a hide of gold; this is an illusion of the sorcerer Maricha. But seeing Sita's longing, Rama "
            "took his golden bow and pursued the swift creature into the dense sal forest. The deer bounded effortlessly, vanishing behind trees "
            "and reappearing on distant ridges, drawing Rama deep into the wilderness. Realizing the creature was a magical demon, Rama notched a divine "
            "arrow and struck it down. As Maricha fell dying, he discarded the deer form and mimicked Rama's voice, shouting in agony: Ha Sita! Ha Lakshmana! "
            "Help me! The echoing cry reached the hermitage, compelling Lakshmana to depart and leaving Sita vulnerable to Ravana's cunning arrival."
        ),
    },
    {
        "tale_id": "RAM-002",
        "tale_type": "EPIC-RAMAYANA",
        "title": "The Devotion of the Little Squirrel on the Rama Setu",
        "region": "Rameshwaram / South India",
        "tradition": "Ramayana",
        "source_collection": "Kamba Ramayanam & Ramcharitmanas Folk Traditions",
        "translator": "Traditional Epic Translation",
        "collection_era": "c. 1100-1500 CE",
        "raw_text": (
            "At the southern shores of the ocean near Rameshwaram, the Vanara army labored to construct the great causeway, Rama Setu, across the "
            "roaring sea to Lanka. Mighty warriors like Hanuman, Sugriva, Angada, and Nila uprooted giant mountain peaks and hurled massive boulders "
            "into the surf, chanting Rama's sacred name. Amidst this thundering labor, a small striped squirrel watched with a heart brimming with "
            "devotion. Desiring to serve Rama, the tiny creature scurried into the waves, soaked its fur, rolled vigorously in the dry beach sand until its "
            "coat was thick with granules, and scampered out onto the newly laid stones to shake the sand into the crevices between the boulders. "
            "Back and forth it ran, tirelessly carrying tiny grains of sand. A giant monkey accidentally tripped over the creature and laughed mockingly: "
            "Get out of the way, little pest, before a boulder crushes you! Rama, observing from a cliff, called the squirrel to his side. Cradling the "
            "trembling creature in his palm, Rama addressed the Vanara army: Do not mock this squirrel. The strength of your arms moves mountains, but "
            "this little one gives all the strength its tiny body possesses out of pure love. Rama gently stroked the squirrel's back with three fingers. "
            "Tradition tells that the three soft white stripes on the back of every Indian palm squirrel remain forever as the imprint of Rama's divine caress."
        ),
    },
    {
        "tale_id": "RAM-003",
        "tale_type": "EPIC-RAMAYANA",
        "title": "Hanuman and the Dronagiri Mountain of Sanjeevani Herbs",
        "region": "Himalayas / Lanka",
        "tradition": "Ramayana",
        "source_collection": "Valmiki Ramayana & Ramcharitmanas — Yuddha Kanda",
        "translator": "Traditional Epic Translation",
        "collection_era": "c. 500 BCE",
        "raw_text": (
            "On the battlefield of Lanka, the prince Lakshmana was struck down by the blazing celestial spear Shakthi hurled by Meghanada, son of "
            "Ravana. Lakshmana fell lifeless to the earth. The physician Sushena examined him and declared: His breath has ceased, but his soul still "
            "lingers. There is only one hope: before the sun rises, four sacred luminous herbs must be fetched from the Dronagiri peak in the high "
            "Himalayas — especially Mrita-Sanjeevani, which restores the dead to life. Hanuman took on a colossal form, leaped from the southern ocean, "
            "and flew like a streak of lightning across the length of Bharatavarsha. Reaching the snow-clad peaks of Dronagiri, Hanuman searched for "
            "the herb. But the mountain spirits, sensing his urgency, hid the herbs in dazzling halos of light so that every plant on the mountain shone "
            "identically. With sunrise rapidly approaching and no time to debate botanical lore, Hanuman roared with thunderous power, dug his hands into "
            "the very foundation of the mountain, sheared the massive Dronagiri peak from its base, and hoisted the entire mountain upon his right palm. "
            "Flying back across the heavens, he landed on the shores of Lanka before dawn. Sushena crushed the Sanjeevani herb and placed its aroma to "
            "Lakshmana's nostrils; Lakshmana opened his eyes, revived and glowing with vitality."
        ),
    },
    {
        "tale_id": "RAM-004",
        "tale_type": "EPIC-RAMAYANA",
        "title": "Shabari's Sweet Berries in the Kishkindha Forest",
        "region": "Kishkindha / South India",
        "tradition": "Ramayana",
        "source_collection": "Ramcharitmanas & Valmiki Ramayana — Aranya Kanda",
        "translator": "Traditional Epic Translation",
        "collection_era": "c. 1500 CE",
        "raw_text": (
            "Near the lotus-filled waters of Lake Pampa in Kishkindha lived an elderly tribal ascetic named Shabari in the hermitage of Sage Matanga. "
            "For decades she had swept the forest paths and gathered wild flowers, faithful to her guru's prophecy that one day Lord Rama would visit her "
            "hut. When Rama and Lakshmana arrived in their wandering search for Sita, Shabari was overwhelmed with tears of joy. She washed their feet with "
            "forest spring water and offered them fresh wild jujube berries (ber) gathered from the thorn bushes. Before handing each berry to Rama, Shabari "
            "bit into it with her toothless mouth to ensure it was not bitter or sour, casting aside the sour ones and offering only the sweetest berries. "
            "Lakshmana frowned, troubled that touched and tasted food was being offered to the scion of Raghu. But Rama smiled with radiant warmth, ate every "
            "tasted berry with deep relish, and proclaimed: I do not value wealth, noble lineage, or ritual purity where love is absent. The simple, "
            "heartfelt devotion of Shabari is the sweetest offering in all the three worlds."
        ),
    },
    {
        "tale_id": "RAM-005",
        "tale_type": "EPIC-RAMAYANA",
        "title": "Jatayu's Valorous Defense of Sita in the Skies",
        "region": "Panchavati / Maharashtra",
        "tradition": "Ramayana",
        "source_collection": "Valmiki Ramayana — Aranya Kanda",
        "translator": "Traditional Epic Translation",
        "collection_era": "c. 500 BCE",
        "raw_text": (
            "As the demon king Ravana fled through the upper skies in his aerial chariot Pushpaka carrying the captive Sita, the aged king of vultures, "
            "Jatayu, perched on a mountain peak, heard her agonizing cries: O noble Jatayu, behold how the wicked lord of Lanka drags me away like a "
            "helpless deer! Though Jatayu was old, frail, and unarmed, he soared into the heavens to fulfill his sacred duty. He blocked Ravana's path, "
            "crying: Desist, king of demons! As long as life pulses in my veins, you shall not carry off the daughter-in-law of Dasharatha! Jatayu "
            "attacked with beak and talons, smashing Ravana's chariot into splinters, slaying his horses, and tearing deep wounds in Ravana's chest. "
            "Enraged by the vulture's ferocity, Ravana drew his enchanted blade, the Chandrahasa, and severed Jatayu's wings and talons. The noble bird "
            "fell bleeding to the rocky earth below. Jatayu held onto his final breaths through agonizing hours until Rama and Lakshmana found him. With his "
            "dying breath, Jatayu informed Rama that Ravana had taken Sita toward the southern ocean, and died peacefully in Rama's arms, honored by Rama "
            "with the final funeral rites of a beloved father."
        ),
    },
    {
        "tale_id": "RAM-006",
        "tale_type": "EPIC-RAMAYANA",
        "title": "Kevat the Boatman Washing the Feet of Rama at the Ganga",
        "region": "Prayag / North India",
        "tradition": "Ramayana",
        "source_collection": "Ramcharitmanas — Ayodhya Kanda",
        "translator": "Goswami Tulsidas Translation",
        "collection_era": "c. 1574 CE",
        "raw_text": (
            "At the beginning of their fourteen-year exile, Rama, Sita, and Lakshmana reached the northern banks of the sacred river Ganga near "
            "Sringaverapura. Rama requested the local boatman, Kevat, to ferry them across the wide, rushing waters. Kevat bowed with hands folded, but "
            "politely refused to let Rama step aboard. He said: My Lord, I know the magic power of your feet! With one touch of your dust, a stone in "
            "the forest turned into a living woman named Ahalya. My wooden boat is my only livelihood; if the touch of your dust turns my boat into a "
            "woman, I cannot support two wives and my children will starve! If you wish to cross in my boat, you must first allow me to wash the dust "
            "from your holy feet with river water. Rama smiled at the boatman's loving pretext and agreed. Kevat brought an earthen basin, tenderly "
            "washed Rama's lotus feet, and drank the holy water with his family. After rowing them safely across to the southern shore, Sita offered her "
            "pearl ring as payment for the ferry. Kevat wept and declined: My Lord, a barber does not charge another barber, nor does a washerman charge "
            "a washerman. Today I have ferried you across the river Ganga; when my time comes, ferry my soul across the ocean of worldly existence, "
            "and we shall be even."
        ),
    },

    # -------------------------------------------------------------------------
    # Mahabharata
    # -------------------------------------------------------------------------
    {
        "tale_id": "MAH-001",
        "tale_type": "EPIC-MAHABHARATA",
        "title": "Yaksha Prashna — Yudhishthira and the Riddles of the Enchanted Pool",
        "region": "Dvaitavana / North India",
        "tradition": "Mahabharata",
        "source_collection": "Vyasa Mahabharata — Aranyaka Parva",
        "translator": "K.M. Ganguli Translation",
        "collection_era": "c. 400 BCE",
        "raw_text": (
            "During their twelve-year forest exile in Dvaitavana, the Pandavas grew parched with thirst. Yudhishthira sent Nakula to find water. Nakula "
            "discovered a crystal-clear pool surrounded by blossoming lotus flowers. As he knelt to drink, an invisible voice from a crane perched on the "
            "bank warned: Do not drink, child, until you have answered my questions! Nakula disregarded the warning, drank, and fell dead. One by one, "
            "Sahadeva, Arjuna, and mighty Bhima followed, ignored the voice, and fell lifeless. Finally Yudhishthira arrived. Seeing his four invincible "
            "brothers dead on the grass, he wept bitterly. The voice spoke again, revealing itself as a Yaksha: Answer my questions, king, or join your "
            "brothers! Yudhishthira bowed humbly: Ask, O spirit. The Yaksha asked: What is swifter than the wind? The mind, answered Yudhishthira. What "
            "is more numerous than blades of grass? Thoughts in the human heart. What is the greatest wonder in the world? Every single day humans witness "
            "countless creatures die, yet everyone lives as though they will live forever. Pleased with his answers, the Yaksha offered to revive one brother. "
            "Yudhishthira chose Nakula, explaining: My father had two wives, Kunti and Madri; since I, Kunti's son, am alive, it is only just that one "
            "son of Madri also lives. The Yaksha revealed himself as Lord Dharma, the god of righteousness and Yudhishthira's celestial father, and restored "
            "all four brothers to life."
        ),
    },
    {
        "tale_id": "MAH-002",
        "tale_type": "EPIC-MAHABHARATA",
        "title": "The Eye of the Wooden Bird — Dronacharya's Test of Supreme Focus",
        "region": "Hastinapura / North India",
        "tradition": "Mahabharata",
        "source_collection": "Vyasa Mahabharata — Adi Parva",
        "translator": "K.M. Ganguli Translation",
        "collection_era": "c. 400 BCE",
        "raw_text": (
            "In the royal training grounds of Hastinapura, the master of archery Dronacharya assembled his royal pupils — the Pandavas and Kauravas — "
            "for a test of skill. Drona had placed a lifelike wooden bird perched high in the branches of a distant mango tree. He called Yudhishthira "
            "first, instructed him to draw his bowstring to his ear, and asked: Tell me, prince, what do you see before you? Yudhishthira replied: I see "
            "the mango tree, the green leaves, the sky, the bird, and you, my teacher. Drona said: Put down your bow; you cannot shoot. Drona called "
            "Duryodhana, Bhima, and Nakula, and each described the forest, the branches, and the body of the bird. Drona dismissed each one in turn. Finally "
            "Drona called Arjuna. Arjuna raised his Gandiva bow and drew the string tight. Drona asked: What do you see, Arjuna? Do you see the tree? No, "
            "Master, replied Arjuna. Do you see the branches or the feathers of the bird? No, Master, I see only the black pupil in the eye of the bird. "
            "Can you see anything else? Nothing else in the world, Master. Drona's heart swelled with pride and he shouted: Shoot! The arrow leaped from the "
            "bowstring and severed the bird's eye cleanly from the tree, establishing Arjuna as the unmatched archer of the age."
        ),
    },
    {
        "tale_id": "MAH-003",
        "tale_type": "EPIC-MAHABHARATA",
        "title": "The Ultimate Sacrifice — Karna's Golden Teeth on the Battlefield",
        "region": "Kurukshetra / Haryana",
        "tradition": "Mahabharata",
        "source_collection": "Mahabharata Folk Lore & Karna Parva Traditions",
        "translator": "Traditional Retelling",
        "collection_era": "c. 400 BCE",
        "raw_text": (
            "On the seventeenth day of the great war of Kurukshetra, the invincible warrior Karna lay mortally wounded in the bloody mud, his chariot "
            "wheel stuck in the earth and his life force draining away into the dusk. Lord Krishna, seeking to demonstrate to Arjuna why Karna was celebrated "
            "across the three worlds as the supreme giver (Dana-Veera Karna), assumed the disguise of a frail, starving Brahmin mendicant and approached the "
            "dying hero. The Brahmin pleaded: O Karna, I have walked through the battlefield seeking alms to perform the sacred rites for my ancestors. "
            "You are renowned as a giver who never turns a beggar away. Give me alms! Karna whispered with cracked lips: Venerable sage, look upon me. "
            "I lie dying on the mud; my weapons are broken, my jewels are gone. I have nothing left to give. The Brahmin turned away in disgust: Then the world "
            "is deceived, for Karna turns away a beggar at his hour of death! Karna called out: Wait, Holy Father! Karna remembered that two of his teeth were "
            "inlaid with pure gold. He picked up a jagged flint stone from the bloody soil, struck his own jaw with agonizing force, and smashed the gold teeth "
            "from his gums. Because they were covered in his own blood, he notched an arrow to his bow, shot it into the dry earth to bring forth a jet of pure "
            "water, washed the golden teeth clean, and offered them on his palm. Krishna discarded his disguise, revealed his divine form, and blessed Karna with eternal glory."
        ),
    },
    {
        "tale_id": "MAH-004",
        "tale_type": "EPIC-MAHABHARATA",
        "title": "Ekalavya and the Silent Guru Dakshina of the Nishada Archer",
        "region": "Forests of Hastinapura",
        "tradition": "Mahabharata",
        "source_collection": "Vyasa Mahabharata — Adi Parva",
        "translator": "K.M. Ganguli Translation",
        "collection_era": "c. 400 BCE",
        "raw_text": (
            "Ekalavya, the young prince of the Nishada forest tribes, longed to master archery under the greatest preceptor in the land, Guru Dronacharya. "
            "He journeyed to the royal academy in Hastinapura, but Drona turned him away because of court allegiance to the Kuru royal family. Undaunted by "
            "rejection, Ekalavya returned to the deep forest, gathered clay from the riverbank, and sculpted an exact statue of Drona beneath a sacred "
            "banyan tree. Every morning at dawn, Ekalavya bowed before the statue of his guru, meditated on his teachings, and practiced archery with fierce, "
            "solitary devotion. One day the Pandavas were hunting in the forest when their hound ran ahead and began barking loudly at Ekalavya's hermitage. "
            "In an instant, seven swift arrows leaped from the forest and filled the dog's open mouth with such extraordinary precision that the animal was "
            "completely silenced without spilling a single drop of blood. Arjuna and Drona inspected the hound in disbelief: no archer alive possessed the "
            "skill to shoot arrows into a barking mouth by sound alone. Drona found Ekalavya practicing before the clay statue. When Ekalavya touched Drona's "
            "feet and called him master, Drona remembered his promise to make Arjuna the greatest archer. Drona asked: If I am your guru, give me my Guru "
            "Dakshina: your right thumb! Without hesitation, sadness, or anger, Ekalavya drew his hunting knife, severed his right thumb, and placed it "
            "reverently at Drona's feet."
        ),
    },
    {
        "tale_id": "MAH-005",
        "tale_type": "EPIC-MAHABHARATA",
        "title": "The Single Grain of Rice — Krishna and Draupadi's Akshaya Patra",
        "region": "Kamyaka Forest",
        "tradition": "Mahabharata",
        "source_collection": "Vyasa Mahabharata — Vana Parva",
        "translator": "K.M. Ganguli Translation",
        "collection_era": "c. 400 BCE",
        "raw_text": (
            "During the forest exile of the Pandavas in Kamyaka, the sun-god Surya gifted Yudhishthira a divine bronze vessel called the Akshaya Patra. "
            "It produced an inexhaustible supply of food every day for guests and ascetics until Draupadi finished her meal and washed the vessel, after which "
            "it ceased until the next dawn. Duryodhana, wishing to bring destruction upon the Pandavas, sent the notoriously short-tempered sage Durvasa and "
            "ten thousand disciples to visit the Pandavas late in the afternoon, just after Draupadi had washed the vessel. Durvasa announced: We are going to "
            "bathe in the river; prepare a feast for ten thousand upon our return, or face my terrible curse! Draupadi wept in despair, for the kitchen was "
            "empty. In agony she prayed to Lord Krishna. In an instant Krishna appeared, smiling: Sister, I have traveled far and am starving; feed me first! "
            "Draupadi showed him the sparkling clean pot. Krishna inspected the rim and found a single tiny speck of spinach leaf and a crushed grain of rice "
            "clinging to the edge. Krishna placed it on his tongue and proclaimed: May the Lord of the Universe be satisfied! At that very moment in the river, "
            "Sage Durvasa and all ten thousand disciples suddenly felt their stomachs filled to bursting, as if they had consumed a thirty-course royal feast. "
            "Ashamed of being unable to eat more, Durvasa and his followers slipped away silently into the forest."
        ),
    },
    {
        "tale_id": "MAH-006",
        "tale_type": "EPIC-MAHABHARATA",
        "title": "Arjuna and the Hunter Shiva on Mount Indrakeela",
        "region": "Indrakeela / Himalayas",
        "tradition": "Mahabharata",
        "source_collection": "Vyasa Mahabharata — Kirata Parva",
        "translator": "K.M. Ganguli Translation",
        "collection_era": "c. 400 BCE",
        "raw_text": (
            "To obtain the supreme celestial weapon Pashupatastra from Lord Shiva, Arjuna climbed the rugged, snow-crested heights of Mount Indrakeela in the "
            "Himalayas. Clad in bark and deer hide, he performed intense austerities, standing on one foot surrounded by sacred fires. A ferocious wild boar, "
            "possessed by the demon Muka, charged toward the hermitage to kill Arjuna. Arjuna seized his bow and loosed an arrow. At the exact same fraction of "
            "a second, an arrow from a rugged forest tribal hunter (Kirata) struck the boar. Both arrows pierced the beast simultaneously. Arjuna claimed the kill, "
            "but the hunter mocked him: You are an ascetic in hermit's garb; what business do you have claiming a hunter's quarry? A furious duel broke out. "
            "Arjuna's arrows shattered against the hunter like raindrops on a cliff; his sword broke on the hunter's helm; his bare-knuckle punches felt like "
            "petals against solid mountain granite. Exhausted and bleeding, Arjuna fashioned a clay Shivalinga on the grass and placed a garland of wild forest "
            "flowers upon it, praying to Shiva for strength. When he looked up, the garland was resting on the hunter's brow! The hunter dissolved into the "
            "radiant form of Lord Shiva with the crescent moon in his matted locks. Shiva smiled: I tested your valor, Arjuna; no mortal matches your courage. "
            "Shiva bestowed the cosmic Pashupatastra weapon upon the bowing prince."
        ),
    },

    # -------------------------------------------------------------------------
    # Renowned Pan-Indian Folk Tales
    # -------------------------------------------------------------------------
    {
        "tale_id": "PAN-020",
        "tale_type": "ATU-178A",
        "title": "The Brahmin's Wife and the Faithful Mongoose",
        "region": "Kashmir / Punjab",
        "tradition": "Panchatantra",
        "source_collection": "Panchatantra — Ryder Translation",
        "translator": "Arthur W. Ryder",
        "collection_era": "c. 200 BCE",
        "raw_text": (
            "In a village near the foothills of Punjab lived a Brahmin named Deva Sharma and his wife. Having no children, they adopted an orphaned "
            "baby mongoose and nurtured it with milk and affection like their own son. In time, the Brahmin's wife gave birth to a healthy baby boy. "
            "Though the mongoose played gently near the cradle, the mother was always suspicious of animal nature. One afternoon, the Brahmin was away "
            "begging for alms, and the mother went to the village well to fetch water, leaving the infant asleep in his crib. While she was away, a deadly "
            "black cobra slithered through a hole in the mud wall toward the baby's cradle. Seeing the danger to his little brother, the faithful mongoose "
            "leaped upon the serpent. A desperate, bloody battle ensued; the mongoose bit the cobra behind the hood, tore it into pieces, and killed it. "
            "Proud of protecting the baby, the mongoose ran to the door to greet the mother, its mouth and paws covered in snake's blood. The mother saw "
            "the blood-smeared animal and jumped to the rash conclusion: The beast has killed my baby! In blind rage and horror, she hurled the heavy stone "
            "water pitcher onto the mongoose, crushing its skull. Rushing into the nursery, she found her baby gurgling happily in the crib and the shredded "
            "cobra lying dead on the floor. She wept bitterly, tearing her hair, for hasty judgment destroys the innocent."
        ),
    },
    {
        "tale_id": "PAN-021",
        "tale_type": "ATU-122",
        "title": "The Blue Jackal — The Indigo Vat and the Forest King",
        "region": "Malwa / Central India",
        "tradition": "Panchatantra",
        "source_collection": "Panchatantra — Ryder Translation",
        "translator": "Arthur W. Ryder",
        "collection_era": "c. 200 BCE",
        "raw_text": (
            "A scrawny, famished jackal named Chandaraka was prowling through a town at midnight looking for food when a pack of fierce street dogs "
            "surrounded him. Fleeing in panic, the jackal leapt through an open window into a dyer's workshop and plunged headfirst into a giant wooden vat "
            "filled with dark blue indigo dye. He submerged completely until the dogs lost his scent and departed. When Chandaraka crawled out of the vat "
            "next morning and looked into a puddle, he was amazed: his fur was dyed an unearthly, brilliant royal sapphire blue! Returning to the jungle, "
            "every creature he met — tigers, leopards, bears, and elephants — fled in utter terror, believing a new demon had descended from the heavens. "
            "Seeing their fear, the clever jackal called out: O forest dwellers, do not tremble! Lord Brahma himself created me with his own hands from "
            "celestial light and crowned me Kakudruma, king of all beasts, to protect this forest! For months the blue jackal lived in royal luxury, dining "
            "on meat brought by lions and tigers while expelling his fellow jackals from his court. But one night under a luminous full moon, a distant pack "
            "of wild jackals began their traditional midnight howl: Oooo-aaah-hooo! Hearing his clan, Chandaraka's fur stood on end; his natural instinct "
            "overpowered his disguise, and he threw his snout to the sky and howled with all his might. The lion and tiger stopped, looked at him, and said: "
            "It is only a jackal! In an instant they fell upon him and tore him to pieces. True nature can never be hidden by outward color."
        ),
    },
    {
        "tale_id": "PAN-022",
        "tale_type": "ATU-225A",
        "title": "Kambugriva — The Talkative Tortoise and the Flying Geese",
        "region": "Magadha",
        "tradition": "Panchatantra",
        "source_collection": "Panchatantra — Ryder Translation",
        "translator": "Arthur W. Ryder",
        "collection_era": "c. 200 BCE",
        "raw_text": (
            "In a lotus lake in the kingdom of Magadha lived a tortoise named Kambugriva, who was close friends with two wild geese named Sankata and Vikata. "
            "The three companions spent every afternoon conversing on the sandy banks. Eventually a severe drought struck the land; rivers dried up and the "
            "lake receded into a muddy pool. The geese told Kambugriva: Dear friend, the water is vanishing. We must fly to a deep mountain lake near Mount Meru "
            "where water never dries, but how can you, who cannot fly, survive here? The tortoise wept and begged them to take him along. The geese devised a "
            "plan: We shall hold the two ends of a strong wooden stick in our beaks, and you must clamp your mouth firmly onto the middle of the stick. As we "
            "fly across the clouds, you must not open your mouth to utter a single syllable, no matter what you see or hear. The tortoise agreed. The two "
            "geese lifted into the sky with the tortoise hanging between them. As they flew over a village, the townspeople looked up and shouted in "
            "astonishment: Look at that miracle! Two birds carrying a round turtle! If it falls, we shall roast it for dinner! Kambugriva grew furious at "
            "the villagers' taunts. Unable to restrain his tongue, he opened his mouth to shout: Eat ashes, fools! The moment he opened his jaws, he lost his "
            "grip on the stick, tumbled from the sky, and shattered upon the stones below."
        ),
    },
    {
        "tale_id": "BEN-001",
        "tale_type": "FOLK-BENGAL",
        "title": "Saat Bhai Champa — The Seven Champa Flowers and Sister Parul",
        "region": "Bengal",
        "tradition": "Bengali Folk",
        "source_collection": "Thakurmar Jhuli — Dakshinaranjan Mitra Majumder",
        "translator": "Traditional Bengali Folklore",
        "collection_era": "c. 1850-1907 CE",
        "raw_text": (
            "Once there was a king of Bengal who had seven wives. The younger queen, who was kind and pure, gave birth to seven handsome sons and a daughter. "
            "But the six elder queens, burning with jealousy, stole the newborn babies in the dark of night, buried them secretly in the ash-heap of the "
            "palace garden, and told the king that the young queen had given birth to mice and crabs. The enraged king banished the poor young queen to live "
            "as a wretched servant in the cow sheds. Months passed, and from the garden ash-heap blossomed seven magnificent white champa trees and a tender "
            "parul flower bush, their fragrant blooms glittering like stars. When the royal gardener approached to pluck the blossoms for the palace temple, "
            "the flowers floated up toward the sky, and a sweet voice sang from the branches: Seven brothers Champa, awaken from your sleep! The parul flower "
            "replied from below: Sister Parul is awake; why do the flowers ascend? The champa blossoms sang: Unless our banished mother comes, we shall not "
            "descend for any king! The king was summoned. Confused, he ordered the banished queen brought to the garden in her tattered rags. As soon as the "
            "weeping mother stretched out her trembling arms, all seven champa blossoms and the parul flower descended into her lap, transforming instantly into "
            "seven handsome young princes and a beautiful princess. The wicked queens were punished, and the family was restored to joyful reign."
        ),
    },
    {
        "tale_id": "KAS-001",
        "tale_type": "FOLK-KASHMIR",
        "title": "The Clever Weaver and the Greedy Merchant of Srinagar",
        "region": "Kashmir",
        "tradition": "Kashmiri Folk",
        "source_collection": "Folk Tales of Kashmir — J. Hinton Knowles",
        "translator": "J. Hinton Knowles",
        "collection_era": "c. 1888 CE",
        "raw_text": (
            "In the winding alleys of old Srinagar by the Jhelum river lived a poor pashmina shawl weaver named Ghulam. To buy wool for a royal shawl, he borrowed "
            "twenty silver rupees from an avaricious moneylender named Pandit Hariram, promising to repay the loan within six months. When the shawl was finished, "
            "Ghulam paid Hariram the twenty silver coins in full. But Hariram smiled slyly and said: You have repaid the silver coins, but during these six months "
            "the silver coins sat on my wooden table and cast a shadow upon my ledger book; you must pay twenty more silver coins for the rent of the shadow! "
            "Ghulam was horrified and brought the dispute before the wise Kashmiri Qazi (judge). The judge listened quietly to Hariram's smug argument that "
            "shadows are valuable property. The judge smiled and said: You are quite right, Hariram. A shadow is a real thing. The judge instructed Ghulam to bring "
            "twenty silver coins and placed them in a crystal glass bowl on the sunny windowsill. The bright Kashmiri sun cast a clear, shimmering shadow of the "
            "silver coins directly onto Hariram's lap. The judge announced: Here is the shadow of twenty silver coins! Take the shadow to your heart's content to "
            "pay for the shadow of your debt, but leave the real coins in the bowl for the weaver! The greedy merchant was laughed out of court by all the townsfolk."
        ),
    },
    {
        "tale_id": "RAJ-004",
        "tale_type": "FOLK-RAJASTHAN",
        "title": "The Loyal Steed Chetak and the Battle of Haldighati",
        "region": "Rajasthan / Marwar",
        "tradition": "Rajasthani Folk",
        "source_collection": "Annals and Antiquities of Rajasthan — James Tod",
        "translator": "Colonel James Tod",
        "collection_era": "c. 1829 CE",
        "raw_text": (
            "In the narrow, yellow-clay pass of Haldighati in the Aravalli hills of Mewar, Maharana Pratap fought a desperate battle against the imperial "
            "army of Emperor Akbar in the scorching summer heat of 1576. Pratap rode his legendary Kathiawari war stallion, Chetak, a blue-grey horse of "
            "extraordinary intelligence and devotion. During the clash, Chetak reared high and planted his forehooves directly upon the forehead of the "
            "imperial war elephant ridden by the enemy general, allowing Pratap to hurl his spear. As Chetak leaped back, a sword blade attached to the "
            "elephant's tusk slashed deeply across the horse's rear leg, severing tendons and muscles. Despite bleeding profusely and in terrible pain, Chetak "
            "refused to collapse. Sensing that his royal master was being surrounded by enemy cavalry, the wounded stallion carried Pratap through the enemy "
            "vanguard at breakneck speed. Reaching a turbulent mountain river ravine twenty-one feet wide, which no normal horse could ever cross, Chetak "
            "gathered all his remaining life force, made a stupendous leap across the chasm, and carried his master to safety on the opposite bank. The moment "
            "Pratap dismounted, Chetak sank to his knees, rested his head in the weeping king's lap, and breathed his last. To this day, a marble cenotaph "
            "stands at the pass, celebrating Chetak as the eternal symbol of unyielding Rajput loyalty."
        ),
    },
]


def main():
    if not CORPUS_PATH.exists():
        print(f"Error: Corpus file not found at {CORPUS_PATH}")
        return

    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        existing = json.load(f)

    existing_ids = {t["tale_id"] for t in existing}
    added = 0
    for tale in NEW_TALES:
        if tale["tale_id"] not in existing_ids:
            existing.append(tale)
            existing_ids.add(tale["tale_id"])
            added += 1

    with open(CORPUS_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    print(f"Successfully added {added} new tales.")
    print(f"Total corpus size: {len(existing)} tales.")


if __name__ == "__main__":
    main()
