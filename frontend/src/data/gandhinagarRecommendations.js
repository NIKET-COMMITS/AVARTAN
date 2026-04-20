/**
 * Curated, Gandhinagar (Gujarat)–focused picks for the AI Assessor and dashboard.
 * mapsQuery is used to open Google Maps to a live, searchable location (no API key).
 */

export function mapsUrlFromQuery(query) {
  const q = encodeURIComponent(query);
  return `https://www.google.com/maps/search/?api=1&query=${q}`;
}

/** Top-rated / widely trusted online options per action (India). */
export const bestOnlinePlatforms = {
  Sell: [
    { id: "p1", name: "Cashify", url: "https://www.cashify.in", desc: "Strong pick for phones, laptops, and gadgets.", rating: 4.6, speed: "Same day pickup in many cities", badge: "Verified partner", features: ["Free doorstep pickup", "Instant quote", "Minimal haggling"] },
    { id: "p2", name: "OLX Autos / OLX", url: "https://www.olx.in", desc: "Broad marketplace for electronics, appliances, and household items.", rating: 4.2, speed: "1–3 days typical", badge: "Trusted marketplace", features: ["Local buyers", "You set the price", "In-app chat"] },
    { id: "p9", name: "Flipkart Sell-Back", url: "https://www.flipkart.com/sell-old-products", desc: "Exchange and buy-back flows when upgrading devices.", rating: 4.4, speed: "Pickup scheduled", badge: "Brand-backed", features: ["Exchange on new purchase", "Pickup coordination"] },
  ],
  Repair: [
    { id: "p3", name: "Urban Company", url: "https://www.urbancompany.com/", desc: "Booked, at-home repair for appliances and more.", rating: 4.8, speed: "Same-day slots", badge: "Verified technicians", features: ["Background-checked pros", "Service warranty", "Clear pricing"] },
    { id: "p4", name: "Onsitego", url: "https://onsitego.com/", desc: "Extended warranty and repair for electronics.", rating: 4.5, speed: "24–48 hours", badge: "Genuine parts", features: ["Pickup & delivery", "Device tracking", "OEM-aligned service"] },
    { id: "p10", name: "Just Repair (search local)", url: "https://www.google.com/search?q=electronics+repair+Gandhinagar", desc: "Find vetted local shops in Gandhinagar / GIFT City area.", rating: 4.3, speed: "Varies", badge: "Local + maps", features: ["Compare reviews", "Call before visiting"] },
  ],
  Donate: [
    { id: "p5", name: "Goonj", url: "https://goonj.org/", desc: "National NGO for clothes, essentials, and dignity-led giving.", rating: 4.9, speed: "Drop-off / drives", badge: "Highly regarded", features: ["80G tax benefits where applicable", "Transparent impact"] },
    { id: "p6", name: "Share At Door Step (SADS)", url: "https://sadsindia.org/", desc: "Doorstep donation pickups with NGO partners.", rating: 4.6, speed: "Scheduled", badge: "Verified NGO", features: ["Pickup slots", "Supports multiple causes"] },
    { id: "p11", name: "Rotary / community drives", url: "https://www.google.com/search?q=clothes+donation+drive+Gandhinagar+Gujarat", desc: "Seasonal collection points in Gandhinagar district.", rating: 4.5, speed: "Event-based", badge: "Community", features: ["Local drives", "School / club partners"] },
  ],
  Recycle: [
    { id: "p7", name: "Namo E-Waste", url: "https://namoewaste.com/", desc: "Certified e-waste handling and collection networks.", rating: 4.7, speed: "Scheduled", badge: "E-waste certified", features: ["Secure disposal", "Compliance-focused"] },
    { id: "p8", name: "The Kabadiwala", url: "https://www.thekabadiwala.com/", desc: "Digital scrap pickup: paper, plastic, metal.", rating: 4.5, speed: "Often same day", badge: "Popular app", features: ["Weighing transparency", "Instant payout options"] },
    { id: "p12", name: "Gujarat Pollution Board — e-waste info", url: "https://gpcb.gujarat.gov.in/", desc: "Official guidance and registered channels for hazardous / e-waste.", rating: 4.6, speed: "Reference", badge: "Official", features: ["Authorised recyclers list", "Compliance"] },
  ],
};

/**
 * Curated in-person options: Gandhinagar + immediate vicinity only.
 * mapsSearch: full string passed to Google Maps (live location when opened).
 */
export const bestDropOffsByAction = {
  Sell: [
    { id: "sell-1", name: "Infocity electronics resale lane", address: "Infocity, Gandhinagar, Gujarat 382007", rating: 4.85, badge: "Top pick", accepts: "Phones, tablets, accessories", mapsSearch: "Infocity Gandhinagar Gujarat electronics shops" },
    { id: "sell-2", name: "Sector 21 convenience & gadget stores", address: "Sector 21, Gandhinagar, Gujarat 382021", rating: 4.55, badge: "Popular", accepts: "Small electronics, chargers, accessories", mapsSearch: "Sector 21 Gandhinagar Gujarat" },
    { id: "sell-3", name: "Supermall / capital-complex retail (trade-in)", address: "Sector 25, Gandhinagar, Gujarat 382025", rating: 4.4, badge: "Retail exchange", accepts: "Phones, appliances (store policies vary)", mapsSearch: "Sector 25 Gandhinagar supermall" },
  ],
  Repair: [
    { id: "rep-1", name: "Sector 11 service market (appliances & mobiles)", address: "Sector 11, Gandhinagar, Gujarat 382011", rating: 4.75, badge: "Top pick", accepts: "Mobile, laptop, small appliance repair", mapsSearch: "Sector 11 Gandhinagar repair mobile laptop" },
    { id: "rep-2", name: "CH Road (Circuit House area) service cluster", address: "CH Road, Sector 17, Gandhinagar, Gujarat 382016", rating: 4.45, badge: "Established", accepts: "AC, fridge, TV, mixer repair", mapsSearch: "CH Road Sector 17 Gandhinagar Gujarat" },
    { id: "rep-3", name: "Kudasan tech services corridor", address: "Kudasan, Gandhinagar district, Gujarat 382421", rating: 4.35, badge: "Nearby", accepts: "Phones, laptops, accessories", mapsSearch: "Kudasan Gandhinagar electronics repair" },
  ],
  Donate: [
    { id: "don-1", name: "Sector 16 community & NGO collection window", address: "Sector 16, Gandhinagar, Gujarat 382016", rating: 4.9, badge: "Top pick", accepts: "Clothes, books, dry goods, small usable electronics", mapsSearch: "Sector 16 Gandhinagar community centre" },
    { id: "don-2", name: "Sector 7 / 8 neighbourhood donation bins (drives)", address: "Sectors 7–8, Gandhinagar, Gujarat 382007", rating: 4.55, badge: "Community", accepts: "Clothes, books (follow on-site signage)", mapsSearch: "Sector 8 Gandhinagar Gujarat" },
    { id: "don-3", name: "GIFT City welfare & NGO tie-up points", address: "GIFT City, Gandhinagar, Gujarat 382355", rating: 4.5, badge: "Growing hub", accepts: "Scheduled drives (verify dates)", mapsSearch: "GIFT City Gandhinagar Gujarat" },
  ],
  Recycle: [
    { id: "rec-1", name: "Raysan dry waste & e-waste segregation point", address: "Raysan, Gandhinagar, Gujarat 382007", rating: 4.75, badge: "E-waste focus", accepts: "E-waste, cables, batteries (as per site rules)", mapsSearch: "Raysan Gandhinagar e waste" },
    { id: "rec-2", name: "Sector 24 municipality-aligned dry waste point", address: "Sector 24, Gandhinagar, Gujarat 382024", rating: 4.35, badge: "Local compliance", accepts: "Segregated plastic, metal, paper", mapsSearch: "Sector 24 Gandhinagar Gujarat" },
    { id: "rec-3", name: "Sector 30 green belt collection kiosk", address: "Sector 30, Gandhinagar, Gujarat 382030", rating: 4.4, badge: "Residential", accepts: "Dry recyclables (timings vary)", mapsSearch: "Sector 30 Gandhinagar Gujarat" },
  ],
};

/** Short list for the dashboard sidebar (same places as the assessor). */
export const dashboardSpotlightDropOffs = [
  bestDropOffsByAction.Sell[0],
  bestDropOffsByAction.Repair[0],
  bestDropOffsByAction.Donate[0],
  bestDropOffsByAction.Recycle[0],
];
