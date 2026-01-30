'use client';

import { useQuery } from '@tanstack/react-query';
import { reviewsApi } from '@/lib/api/reviews';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Star } from 'lucide-react';
import { formatDate } from '@/lib/utils/formatters';
import { motion } from 'framer-motion';
import { SkeletonTable } from '@/components/ui/loading-skeleton';
import { EmptyState } from '@/components/ui/empty-state';

export default function ReviewsPage() {
  const { data: reviews, isLoading } = useQuery({
    queryKey: ['reviews'],
    queryFn: () => reviewsApi.getAll({ limit: 100 }),
  });

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
          Reviews
        </h1>
        <p className="text-muted-foreground mt-2">User feedback and ratings</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="rounded-lg border bg-card shadow-md overflow-hidden"
      >
        {isLoading ? (
          <div className="p-6">
            <SkeletonTable rows={5} />
          </div>
        ) : reviews && reviews.length > 0 ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Driver</TableHead>
                <TableHead>Rating</TableHead>
                <TableHead>Comment</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {reviews.map((review, index) => (
                <motion.tr
                  key={review.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.03 }}
                  className="border-b hover:bg-muted/50 transition-colors"
                >
                  <TableCell className="font-medium">Driver #{review.driver_id}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <Star
                          key={i}
                          className={`h-4 w-4 transition-colors ${
                            i < review.rating
                              ? 'fill-yellow-400 text-yellow-400'
                              : 'text-gray-300 dark:text-gray-600'
                          }`}
                        />
                      ))}
                      <span className="ml-1 font-medium">({review.rating})</span>
                    </div>
                  </TableCell>
                  <TableCell className="max-w-md">{review.comment || <span className="text-muted-foreground italic">No comment</span>}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{review.review_type}</Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{formatDate(review.created_at)}</TableCell>
                </motion.tr>
              ))}
            </TableBody>
          </Table>
        ) : (
          <EmptyState
            icon={Star}
            title="No reviews found"
            description="Reviews will appear here once users submit feedback"
          />
        )}
      </motion.div>
    </div>
  );
}
