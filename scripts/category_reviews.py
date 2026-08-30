"""Category-aware review lines for grounded seed evidence."""

CATEGORY_REVIEWS: dict[str, dict[str, list[str]]] = {
    "Dresses": {
        "positive_fit": [
            "The dress fits true to size and drapes well.",
            "Length is perfect for a casual day out.",
            "Waist sits comfortably — not too tight.",
        ],
        "negative_fit": [
            "Runs small around the bust — size up if between sizes.",
            "Hem is shorter than expected for a midi dress.",
            "Fit is tighter around the hips than the size chart suggests.",
        ],
        "positive_fabric": [
            "Fabric feels light and breathable for summer.",
            "The viscose blend moves nicely and is not stiff.",
            "Material has a soft hand-feel against the skin.",
        ],
        "negative_fabric": [
            "Fabric is thinner than it looks online.",
            "Lining would help — material is slightly see-through.",
            "Polyester feels a bit synthetic after a few washes.",
        ],
        "positive_quality": [
            "Stitching along the seams looks neat and secure.",
            "Zipper and finishing details feel well done.",
            "No loose threads — good construction for the price.",
        ],
        "negative_quality": [
            "Seam near the armhole started fraying after two wears.",
            "Zipper catches occasionally at the back.",
            "Print alignment is slightly off at the side seams.",
        ],
        "positive_value": [
            "Good dress for the sale price — would buy again.",
            "Solid everyday dress at this discount.",
            "Fair value compared to similar dresses on my Wishlist.",
        ],
        "negative_value": [
            "Fabric quality does not justify full MRP.",
            "Would wait for a deeper discount on this style.",
            "Better options exist at this price point.",
        ],
        "positive_appearance": [
            "Floral print looks like the website photos.",
            "Colour is vibrant and flattering in person.",
            "Got compliments wearing this to brunch.",
        ],
        "negative_appearance": [
            "Colour is duller than shown on the product page.",
            "Print scale looks different from the listing image.",
            "Looks simpler in person than the photos suggest.",
        ],
    },
    "Sneakers": {
        "positive_fit": [
            "True to size for running — toe box feels roomy.",
            "Snug heel lock without slipping on runs.",
            "Comfortable width for daily wear.",
        ],
        "negative_fit": [
            "Runs half a size small — order up for running.",
            "Narrow fit — wide feet may feel cramped.",
            "Heel rubs slightly on longer walks.",
        ],
        "positive_fabric": [
            "Mesh upper breathes well during workouts.",
            "Lightweight feel — good for long runs.",
            "Upper flexes naturally with each stride.",
        ],
        "negative_fabric": [
            "Mesh feels thin in colder weather.",
            "Upper creases noticeably after a few weeks.",
            "Not much structure around the midfoot.",
        ],
        "positive_quality": [
            "Outsole grip is reliable on wet pavement.",
            "Cushioning still feels springy after a month.",
            "Build quality matches other trainers in this range.",
        ],
        "negative_quality": [
            "Outsole wore down faster than expected.",
            "Glue line visible near the midsole.",
            "Laces frayed quickly with regular use.",
        ],
        "positive_value": [
            "Strong value for a daily running shoe.",
            "Worth it at the current discount.",
            "Good trainer if you want balance of price and comfort.",
        ],
        "negative_value": [
            "Premium models offer better cushioning for slightly more.",
            "Not worth full price — wait for a sale.",
            "Cheaper sneakers feel similar for casual use.",
        ],
        "positive_appearance": [
            "Colourway looks exactly like the photos.",
            "Clean design — easy to pair with gym wear.",
            "Gets noticed — sharp look for lifestyle wear too.",
        ],
        "negative_appearance": [
            "White panels scuff easily.",
            "Colour is more muted than the website.",
            "Bulkier silhouette than expected from photos.",
        ],
    },
    "Tops": {
        "positive_fit": [
            "T-shirt fits true to size across the chest.",
            "Slim fit sits well without pulling at the shoulders.",
            "Regular fit is comfortable for all-day wear.",
        ],
        "negative_fit": [
            "Slim fit runs tight — consider sizing up.",
            "Length is shorter than typical crew necks.",
            "Shoulders feel narrow for a relaxed fit label.",
        ],
        "positive_fabric": [
            "Cotton feels soft and breathable.",
            "Fabric weight is ideal for Indian summers.",
            "Holds shape after several washes.",
        ],
        "negative_fabric": [
            "Cotton is thinner than expected.",
            "Fabric pills slightly after a few washes.",
            "Material feels stiff before the first wash.",
        ],
        "positive_quality": [
            "Neckline stitching is clean and flat.",
            "Print has not cracked after washing.",
            "Good basic tee for the price.",
        ],
        "negative_quality": [
            "Neckline stretched out after a month.",
            "Print started fading after three washes.",
            "Hem stitching came loose on one side.",
        ],
        "positive_value": [
            "Excellent value for an everyday tee.",
            "Worth stocking up during the sale.",
            "Good price for the cotton quality.",
        ],
        "negative_value": [
            "Similar tees available cheaper elsewhere.",
            "Quality does not match the brand premium.",
            "Would only buy on discount.",
        ],
        "positive_appearance": [
            "Print/colour matches the listing.",
            "Looks good paired with jeans or chinos.",
            "Colour has held up well so far.",
        ],
        "negative_appearance": [
            "Print placement differs from the photo.",
            "Colour is darker than shown online.",
            "Graphic looks smaller in person.",
        ],
    },
    "Jeans": {
        "positive_fit": [
            "Slim fit is true to size at the waist.",
            "Tapered leg sits well over sneakers.",
            "Comfortable stretch for sitting all day.",
        ],
        "negative_fit": [
            "Waist runs tight — size up if between sizes.",
            "Taper is aggressive — not ideal for muscular thighs.",
            "Inseam runs long on shorter frames.",
        ],
        "positive_fabric": [
            "Denim has a good weight — not too thin.",
            "Stretch denim moves comfortably.",
            "Fade wash looks natural.",
        ],
        "negative_fabric": [
            "Denim feels stiff for the first few wears.",
            "Colour bleeds slightly on first wash.",
            "Stretch loses recovery after heavy use.",
        ],
        "positive_quality": [
            "Rivets and pockets feel sturdy.",
            "Stitching on the fly is solid.",
            "Holding up well after regular wear.",
        ],
        "negative_quality": [
            "Belt loops feel flimsy.",
            "Knee bagging appeared sooner than expected.",
            "Button felt loose after a few weeks.",
        ],
        "positive_value": [
            "Good jeans for the current price.",
            "Fair deal compared to other denim on my Wishlist.",
            "Worth it if you need a reliable daily pair.",
        ],
        "negative_value": [
            "Full MRP feels high for the denim weight.",
            "Better reviewed options near this price.",
            "Would wait for a deeper cut.",
        ],
        "positive_appearance": [
            "Wash matches the product photos.",
            "Classic look — easy to dress up or down.",
            "Colour has stayed consistent after washes.",
        ],
        "negative_appearance": [
            "Wash is lighter than the website images.",
            "Fade pattern looks uneven in person.",
            "Dark wash looks almost black online but navy in hand.",
        ],
    },
    "Handbags": {
        "positive_fit": [
            "Strap length works well for crossbody wear.",
            "Tote fits a laptop and daily essentials comfortably.",
            "Compact size is perfect for evenings out.",
        ],
        "negative_fit": [
            "Strap is shorter than expected.",
            "Interior pockets are smaller than useful.",
            "Does not fit a 13-inch laptop despite photos.",
        ],
        "positive_fabric": [
            "Faux leather feels supple, not plasticky.",
            "Lining material is smooth and easy to wipe.",
            "Hardware feels solid for the price tier.",
        ],
        "negative_fabric": [
            "Leather-look material creases quickly.",
            "Interior lining is thin.",
            "Strap attachment feels less sturdy than expected.",
        ],
        "positive_quality": [
            "Zips glide smoothly — no snagging.",
            "Magnetic closure on the flap is secure.",
            "Stitching around handles is even.",
        ],
        "negative_quality": [
            "Zip pull came loose after a few weeks.",
            "Colour on the strap faded unevenly.",
            "Bottom studs fell off with light use.",
        ],
        "positive_value": [
            "Good bag for everyday office use at this price.",
            "Solid pick if you want a budget-friendly tote.",
            "Worth the discount for a secondary bag.",
        ],
        "negative_value": [
            "Premium leather bags feel much sturdier for double the price.",
            "Not worth full MRP given the material.",
            "Cheaper sling bags offer similar capacity.",
        ],
        "positive_appearance": [
            "Colour and shape match the listing photos.",
            "Looks more expensive than it is.",
            "Neutral tone goes with most outfits.",
        ],
        "negative_appearance": [
            "Tan shade is more orange than shown online.",
            "Shape collapses when not fully packed.",
            "Logo placement looks different from the photo.",
        ],
    },
    "Kurtas": {
        "positive_fit": [
            "Kurta length is appropriate for regular wear.",
            "Relaxed fit is comfortable for all-day use.",
            "Shoulder and chest fit true to size.",
        ],
        "negative_fit": [
            "Runs long — alteration may be needed.",
            "Chest fit is tighter than expected.",
            "Sleeves are shorter than typical kurtas.",
        ],
        "positive_fabric": [
            "Cotton feels breathable in humid weather.",
            "Embroidery does not scratch the skin.",
            "Fabric drapes well for an Anarkali cut.",
        ],
        "negative_fabric": [
            "Cotton is thinner than festive wear should be.",
            "Embroidery threads snag easily.",
            "Material wrinkles quickly after washing.",
        ],
        "positive_quality": [
            "Embroidery stitching is neat.",
            "Colour fastness held after two gentle washes.",
            "Neck finishing looks clean.",
        ],
        "negative_quality": [
            "Loose thread on the collar after first wash.",
            "Embroidery colour bled slightly.",
            "Buttons feel flimsy.",
        ],
        "positive_value": [
            "Good festive-casual kurta for the price.",
            "Fair value for cotton ethnic wear.",
            "Worth it on discount for office ethnic days.",
        ],
        "negative_value": [
            "Embroidery quality does not justify full MRP.",
            "Similar kurtas available cheaper locally.",
            "Would buy only during sale.",
        ],
        "positive_appearance": [
            "Print and embroidery match the photos.",
            "Colour is rich and festive in person.",
            "Looks elegant for family gatherings.",
        ],
        "negative_appearance": [
            "Print density is lower than shown online.",
            "Colour is paler than the listing.",
            "Embroidery pattern differs slightly from photos.",
        ],
    },
    "Jackets": {
        "positive_fit": [
            "Jacket fits true to size with room for layering.",
            "Sleeve length is spot on.",
            "Bomber cut sits well at the waist.",
        ],
        "negative_fit": [
            "Runs large — consider sizing down.",
            "Sleeves are long on shorter arms.",
            "Tight across the shoulders in usual size.",
        ],
        "positive_fabric": [
            "Denim has a good mid-weight feel.",
            "Puffer fill is light but warm enough for evenings.",
            "Windcheater fabric blocks light rain.",
        ],
        "negative_fabric": [
            "Denim is stiff until broken in.",
            "Puffer shell feels thin.",
            "Inner lining is not breathable for long wear.",
        ],
        "positive_quality": [
            "Zips and snaps feel durable.",
            "Quilting on the puffer is even.",
            "Hood stitching is secure.",
        ],
        "negative_quality": [
            "Zip caught on lining on first use.",
            "Faux leather started peeling at the cuffs.",
            "Seam tape visible inside.",
        ],
        "positive_value": [
            "Solid jacket for transitional weather at this price.",
            "Good layering piece for the discount.",
            "Worth it if you need a versatile outer layer.",
        ],
        "negative_value": [
            "Premium brands offer better insulation for slightly more.",
            "Not warm enough to justify full MRP.",
            "Cheaper windcheaters perform similarly.",
        ],
        "positive_appearance": [
            "Wash and cut match the product photos.",
            "Classic denim jacket look — pairs with everything.",
            "Colour has not faded after light use.",
        ],
        "negative_appearance": [
            "Denim wash is darker than online.",
            "Puffer looks bulkier in person.",
            "Leather finish looks more matte than photos.",
        ],
    },
    "Watches": {
        "positive_fit": [
            "Strap adjusts easily to wrist size.",
            "Case size looks proportional on a medium wrist.",
            "Lightweight enough for daily wear.",
        ],
        "negative_fit": [
            "Case is large on smaller wrists.",
            "Strap holes are spaced too far apart.",
            "Clasp feels sharp against the skin.",
        ],
        "positive_fabric": [
            "Strap material is comfortable for long wear.",
            "Glass face has resisted minor scratches.",
            "Dial is easy to read in sunlight.",
        ],
        "negative_fabric": [
            "Strap stiff until broken in.",
            "Screen visibility is poor in bright light.",
            "Band collects sweat marks quickly.",
        ],
        "positive_quality": [
            "Timekeeping has been accurate so far.",
            "Buttons/chrono functions work smoothly.",
            "Feels solid for the price segment.",
        ],
        "negative_quality": [
            "Strap pin came loose within a month.",
            "Smartwatch battery drains faster than claimed.",
            "Second hand ticks loudly.",
        ],
        "positive_value": [
            "Good everyday watch for the sale price.",
            "Smartwatch features are fair at this discount.",
            "Worth it as a gift in this range.",
        ],
        "negative_value": [
            "Fossil-tier build at a higher price — wait for sale.",
            "Battery life does not justify full MRP.",
            "Better specs available in competitors near this price.",
        ],
        "positive_appearance": [
            "Dial colour matches the listing.",
            "Looks sharper in person than photos.",
            "Rose gold finish is subtle and elegant.",
        ],
        "negative_appearance": [
            "Dial looks smaller in photos than in person.",
            "Strap colour differs from the website.",
            "Finish shows fingerprints easily.",
        ],
    },
    "Shorts": {
        "positive_fit": [
            "Waist fits true with the drawstring.",
            "Length is good for gym and casual wear.",
            "Relaxed fit allows easy movement.",
        ],
        "negative_fit": [
            "Waist runs tight — size up.",
            "Inseam is shorter than expected.",
            "Leg opening is narrower than photos suggest.",
        ],
        "positive_fabric": [
            "Quick-dry fabric works for training.",
            "Chino cotton is soft and breathable.",
            "Denim shorts have a comfortable stretch.",
        ],
        "negative_fabric": [
            "Synthetic fabric feels hot in summer.",
            "Chino is thinner than expected.",
            "Denim fade looks uneven.",
        ],
        "positive_quality": [
            "Pockets are deep and secure.",
            "Stitching on the hem is clean.",
            "Drawcord has not frayed.",
        ],
        "negative_quality": [
            "Pocket stitching came loose.",
            "Colour faded after a few washes.",
            "Zip fly sticks occasionally.",
        ],
        "positive_value": [
            "Good training shorts for the price.",
            "Fair summer staple at this discount.",
            "Worth picking up during the sale.",
        ],
        "negative_value": [
            "Nike-tier shorts feel sturdier for a bit more.",
            "Not worth full MRP.",
            "Similar shorts cheaper in multi-packs.",
        ],
        "positive_appearance": [
            "Colour matches the listing.",
            "Clean look for gym or casual outings.",
            "Denim wash looks as pictured.",
        ],
        "negative_appearance": [
            "Colour is brighter online than in hand.",
            "Logo placement differs from photos.",
            "Fabric sheen looks different in person.",
        ],
    },
    "Sunglasses": {
        "positive_fit": [
            "Frames sit comfortably on the nose bridge.",
            "Unisex size works for medium faces.",
            "Lightweight — no pressure behind the ears.",
        ],
        "negative_fit": [
            "Slides down on a narrow nose.",
            "Arms feel tight on wider heads.",
            "Cat-eye shape suits smaller faces only.",
        ],
        "positive_fabric": [
            "Lenses cut glare well in sunlight.",
            "Hinges feel smooth and sturdy.",
            "UV protection seems effective for daily driving.",
        ],
        "negative_fabric": [
            "Lenses scratch easily without a case.",
            "Hinges feel loose after a few weeks.",
            "Polarisation is weaker than expected.",
        ],
        "positive_quality": [
            "Comes with a usable carry pouch.",
            "Frame finish has not chipped.",
            "Clear vision with minimal distortion.",
        ],
        "negative_quality": [
            "Screw fell out of the hinge.",
            "Lens coating started peeling at the edge.",
            "Case zipper broke quickly.",
        ],
        "positive_value": [
            "Good style for the discount price.",
            "Fair alternative to premium aviators on sale.",
            "Worth it as a backup pair.",
        ],
        "negative_value": [
            "Ray-Ban quality is noticeably better at full price.",
            "Not worth MRP for the lens clarity.",
            "Cheaper frames feel similar for occasional use.",
        ],
        "positive_appearance": [
            "Frame shape matches the photos.",
            "Classic aviator look — versatile.",
            "Tint colour is as shown online.",
        ],
        "negative_appearance": [
            "Tint is darker than the website suggests.",
            "Frame size looks larger in photos.",
            "Gold finish is more yellow in person.",
        ],
    },
    "Activewear": {
        "positive_fit": [
            "Leggings stay in place during squats.",
            "Sports bra offers medium support as described.",
            "Track pants fit true with a tapered leg.",
        ],
        "negative_fit": [
            "Leggings roll down at the waist during cardio.",
            "Sports bra runs small in the band.",
            "Tank armholes are tighter than expected.",
        ],
        "positive_fabric": [
            "Sweat-wicking fabric dries quickly after gym.",
            "Four-way stretch moves with yoga flows.",
            "Material is opaque during bends.",
        ],
        "negative_fabric": [
            "Fabric becomes sheer when stretched.",
            "Material retains odour after intense sessions.",
            "Tank fabric is thinner than gym brands.",
        ],
        "positive_quality": [
            "Flat seams reduce chafing on long runs.",
            "Waistband elastic has held shape.",
            "Stitching on the sports bra is secure.",
        ],
        "negative_quality": [
            "Waistband stitching came loose.",
            "Logo cracked after washing.",
            "Seams irritated skin on longer workouts.",
        ],
        "positive_value": [
            "Good gym basics for the sale price.",
            "Fair quality compared to other activewear saved.",
            "Worth it for starter workout kit.",
        ],
        "negative_value": [
            "Nike/Adidas tiers feel more durable for slightly more.",
            "Not worth full MRP for the fabric weight.",
            "Cheaper Decathlon options feel similar.",
        ],
        "positive_appearance": [
            "Colour matches the listing.",
            "Flattering fit for gym selfies.",
            "Clean minimal look.",
        ],
        "negative_appearance": [
            "Colour fades after repeated washes.",
            "Fit looks different from model photos.",
            "Logo placement differs from listing.",
        ],
    },
    "Sandals": {
        "positive_fit": [
            "Slides are true to size for casual wear.",
            "Flat sandals are comfortable for short walks.",
            "Straps adjust to a secure fit.",
        ],
        "negative_fit": [
            "Slides run narrow — wide feet beware.",
            "Heel height is higher than expected.",
            "Straps rub on the first few wears.",
        ],
        "positive_fabric": [
            "Footbed cushioning is soft enough for errands.",
            "Strap material has not cracked.",
            "Outdoor sandal grip is decent on dry trails.",
        ],
        "negative_fabric": [
            "Footbed flattens after a few weeks.",
            "Synthetic straps feel stiff initially.",
            "Sole is slippery on wet tiles.",
        ],
        "positive_quality": [
            "Stitching on straps is holding up.",
            "Buckle hardware feels solid.",
            "Slides have survived daily pool use.",
        ],
        "negative_quality": [
            "Strap stitching came undone.",
            "Heel block scuffed quickly.",
            "Outsole wore smooth within a month.",
        ],
        "positive_value": [
            "Good budget slides for home and gym.",
            "Fair price for occasional wear sandals.",
            "Worth the discount for vacation use.",
        ],
        "negative_value": [
            "Premium sandals last longer for double the price.",
            "Not worth MRP for daily commuting.",
            "Cheaper slides feel similar for indoor use.",
        ],
        "positive_appearance": [
            "Embellishments match the photos.",
            "Neutral colour goes with most outfits.",
            "Block heel looks elegant in person.",
        ],
        "negative_appearance": [
            "Embellishments look cheaper in hand.",
            "Colour is more beige than gold online.",
            "Sole looks bulkier than photos.",
        ],
    },
}

# Fallback for generic templates when category missing
GENERIC_REVIEWS = {
    "positive_fit": ["True to size and fits comfortably.", "Perfect fit for my usual size."],
    "negative_fit": ["Runs small — order one size up.", "Fit is tighter than expected."],
    "positive_fabric": ["Fabric feels soft and breathable.", "Material quality is good for the price."],
    "negative_fabric": ["Fabric feels thin.", "Material is stiff before washing."],
    "positive_quality": ["Stitching and finish look durable.", "Well made compared to similar items."],
    "negative_quality": ["Stitching came loose after a few wears.", "Zipper quality is disappointing."],
    "positive_value": ["Great value at this sale price.", "Worth the money for everyday use."],
    "negative_value": ["Overpriced for the quality received.", "Would wait for a deeper discount."],
    "positive_appearance": ["Looks like the product photos.", "Colour matches the listing."],
    "negative_appearance": ["Colour is duller than the website.", "Looks different in person."],
}
