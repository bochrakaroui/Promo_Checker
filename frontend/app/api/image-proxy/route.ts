import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const imageUrl = searchParams.get('url');

  if (!imageUrl) {
    return new NextResponse('Missing image URL parameter', { status: 400 });
  }

  try {
    console.log('Fetching image:', imageUrl);

    // Fetch the image from the external source
    const response = await fetch(imageUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': new URL(imageUrl).origin,
      },
    });

    if (!response.ok) {
      console.error('Failed to fetch image:', response.status, response.statusText);
      return new NextResponse(`Failed to fetch image: ${response.statusText}`, { 
        status: response.status 
      });
    }

    // Get the image data
    const imageBuffer = await response.arrayBuffer();
    const contentType = response.headers.get('content-type') || 'image/jpeg';

    console.log('Image fetched successfully:', contentType, imageBuffer.byteLength, 'bytes');

    // Return the image with appropriate headers
    return new NextResponse(imageBuffer, {
      headers: {
        'Content-Type': contentType,
        'Cache-Control': 'public, max-age=86400, immutable', // Cache for 24 hours
        'Access-Control-Allow-Origin': '*',
      },
    });
  } catch (error) {
    console.error('Error fetching image:', error);
    return new NextResponse(`Error fetching image: ${error instanceof Error ? error.message : 'Unknown error'}`, { 
      status: 500 
    });
  }
}