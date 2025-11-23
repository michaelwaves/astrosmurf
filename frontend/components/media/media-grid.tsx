"use client"

import Image from "next/image"
import { useState } from "react"
import { useSession } from "next-auth/react"
import { fetchAllMedia, fetchArticleWithMedia } from "@/lib/db/actions"
import { Button } from "@/components/ui/button"
import { Share2, Loader2, Check } from "lucide-react"

type MediaItem = Awaited<ReturnType<typeof fetchAllMedia>>[number] | Awaited<ReturnType<typeof fetchArticleWithMedia>>["media"][number]

interface MediaGridProps {
    media: MediaItem[]
}

export function MediaGrid({ media }: MediaGridProps) {
    const { data: session } = useSession()
    const [postingId, setPostingId] = useState<number | null>(null)
    const [postedIds, setPostedIds] = useState<Set<number>>(new Set())

    const handlePostToX = async (mediaId: number) => {
        if (!session?.user?.id) {
            alert("Please sign in to post to X")
            return
        }

        setPostingId(mediaId)

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/x_post`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user_id: Number(session.user.id),
                    media_id: mediaId,
                    text: "",
                }),
            })

            if (!response.ok) {
                throw new Error("Failed to post to X")
            }

            setPostedIds(prev => new Set(prev).add(mediaId))
        } catch (error) {
            alert(error instanceof Error ? error.message : "Failed to post to X")
        } finally {
            setPostingId(null)
        }
    }

    if (media.length === 0) {
        return (
            <div className="text-center py-12 text-muted-foreground">
                No media found
            </div>
        )
    }

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {media.map((item) => (
                <div
                    key={item.id}
                    className="relative aspect-square rounded-lg overflow-hidden bg-gray-100 hover:shadow-lg transition-shadow group"
                >
                    {item.media_type === "image" ? (
                        <Image
                            src={item.media_url}
                            alt={item.prompt || "Generated media"}
                            fill
                            className="object-cover"
                            sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                        />
                    ) : (
                        <video
                            src={item.media_url}
                            className="w-full h-full object-cover"
                            controls
                        />
                    )}

                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                            size="sm"
                            onClick={() => handlePostToX(item.id)}
                            disabled={postingId === item.id || postedIds.has(item.id)}
                            className="bg-black/80 hover:bg-black text-white"
                        >
                            {postingId === item.id ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : postedIds.has(item.id) ? (
                                <>
                                    <Check className="h-4 w-4 mr-1" />
                                    Posted
                                </>
                            ) : (
                                <>
                                    <Share2 className="h-4 w-4 mr-1" />
                                    Post to X
                                </>
                            )}
                        </Button>
                    </div>

                    {item.prompt && (
                        <div className="absolute bottom-0 left-0 right-0 bg-black/70 p-2 text-white text-xs">
                            <p className="line-clamp-2">{item.prompt}</p>
                        </div>
                    )}
                </div>
            ))}
        </div>
    )
}
