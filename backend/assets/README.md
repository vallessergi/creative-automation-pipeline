# Assets Directory

This directory contains existing product assets that will be reused in campaign generation.

## Current Structure:

```
assets/
├── water/
│   └── (Place water bottle images here: bottle.jpg, product_shot.png, etc.)
└── coca_cola/
    └── (Place Coca-Cola images here: can_image.jpg, bottle.png, etc.)
```

## Usage:

1. **Place Product Images**: Add actual product photos in respective folders
2. **Supported Formats**: .jpg, .jpeg, .png, .webp
3. **Naming**: Any filename works - system scans all images in folder
4. **Automatic Detection**: System will find and reuse these assets instead of generating new ones

## Example:

For "Water" product:
- Place images in `assets/water/`
- System automatically detects and reuses for all aspect ratios (1:1, 9:16, 16:9)
- No GenAI generation needed - saves cost and uses real product photos

For "Coca Cola" product:  
- Place images in `assets/coca_cola/`
- System converts spaces to underscores for folder names
- Reuses existing brand imagery when available