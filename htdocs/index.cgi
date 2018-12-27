#!/usr/bin/env perl

use utf8;
use strict;
use warnings;

use 5.16.0;
no warnings 'experimental::smartmatch';

use CGI ':standard';
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use DBI;
use HTML::Entities;
use POSIX 'ceil';
use SQL::Abstract::Limit;
use Template;

my $dbh;
my $debug = 0;
my $title = 'IRCTube :: YouTube video aggregation on IRC';

my $ttvars = {
   mainurl => 'https://irctube.lifeisabug.com',
   numvids => 25,
};

my %ttopts = (
   INCLUDE_PATH => '/srv/www/irctube.lifeisabug.com/templates/',
   PRE_CHOMP    => 2,
   POST_CHOMP   => 2,
);

my %sql = (
   host  => 'localhost',
   db    => 'youtube',
   table => 'youtube',
   user  => 'youtube',
   pass  => '',
);

my %categories = (
    1 => 'Film & Animation',
    2 => 'Autos & Vehicles',
   10 => 'Music',
   15 => 'Pets & Animals',
   17 => 'Sports',
#   18 => 'Short Movies',
   19 => 'Travel & Events',
   20 => 'Gaming',
#   21 => 'Videoblogging',
   22 => 'People & Blogs',
   23 => 'Comedy',
   24 => 'Entertainment',
   25 => 'News & Politics',
   26 => 'Howto & Style',
   27 => 'Education',
   28 => 'Science & Technology',
   29 => 'Nonprofits & Activism',
   30 => 'Movies',
#   31 => 'Anime/Animation',
#   32 => 'Action/Adventure',
#   33 => 'Classics',
#   34 => 'Comedy',
#   35 => 'Documentary',
#   36 => 'Drama',
#   37 => 'Family',
#   38 => 'Foreign',
#   39 => 'Horror',
#   40 => 'Sci-Fi/Fantasy',
#   41 => 'Thriller',
#   42 => 'Shorts',
   43 => 'Shows',
   44 => 'Trailers',
);

croak("template folder $ttopts{INCLUDE_PATH} does not exist") unless (-e $ttopts{INCLUDE_PATH});

my $sql = SQL::Abstract::Limit->new(limit_dialect => 'LimitXY');
my $tt  = Template->new(\%ttopts);

my $qcategory   = param('category');
my $qchannel    = param('channel');
my $qdest       = param('dest');
my $qfiltermode = param('filtermode');
my $qnetwork    = param('network');
my $qnickname   = param('nickname');
my $qpage       = param('page');
my $qrss        = param('rss');
my $qvid        = param('v');

$qdest = 'index' unless ($qdest);
$qpage = 1 unless ($qpage && $qpage >= 1);

$$ttvars{category}   = $qcategory;
$$ttvars{channel}    = $qchannel;
$$ttvars{dest}       = $qdest;
$$ttvars{filtermode} = $qfiltermode;
$$ttvars{network}    = $qnetwork;
$$ttvars{nickname}   = $qnickname;
$$ttvars{page}       = $qpage;

sub duration {
   my $sec = shift;

   return '?' unless ($sec);

   my @gmt = gmtime($sec);

   $gmt[5] -= 70;
   return   ($gmt[5] ?                                                        $gmt[5].' yr' .($gmt[5] > 1 ? 's' : '') : '').
            ($gmt[7] ? ($gmt[5]                                  ? ', ' : '').$gmt[7].' d'  .($gmt[7] > 1 ? 's' : '') : '').
            ($gmt[2] ? ($gmt[5] || $gmt[7]                       ? ', ' : '').$gmt[2].' hr' .($gmt[2] > 1 ? 's' : '') : '').
            ($gmt[1] ? ($gmt[5] || $gmt[7] || $gmt[2]            ? ', ' : '').$gmt[1].' min'.($gmt[1] > 1 ? 's' : '') : '').
            ($gmt[0] ? ($gmt[5] || $gmt[7] || $gmt[2] || $gmt[1] ? ', ' : '').$gmt[0].' sec'.($gmt[0] > 1 ? 's' : '') : '');
}

sub mysql_connect {
   $dbh = DBI->connect("DBI:mysql:$sql{db}:$sql{host}", $sql{user}, $sql{pass},
          {RaiseError => 1, mysql_auto_reconnect => 1, mysql_enable_utf8 => 1});
}

sub mysql_disconnect {
   $dbh->disconnect;
}

sub pairwise_walk(&@) {
   my ($code, $prev) = (shift, shift);
   my @ret;

   push(@ret, $prev);

   for(@_) {
      push(@ret, $code->(local ($a, $b) = ($prev, $_)));
      $prev = $_;
   }

   return @ret;
}

sub printheader {
   print header(
      -cache_control => 'no-cache, no-store, must-revalidate',
      -charset       => 'utf-8',
   );
}

mysql_connect();

my %where;

if ($qvid && !$qrss) {
   $where{vid} = $qvid;
}
else {
   $where{category}  = $qcategory if ($qcategory);
   $where{channel}   = $qchannel  if ($qchannel);
   $where{network}   = $qnetwork  if ($qnetwork);
   $where{nickname}  = $qnickname if ($qnickname);
}

my ($stmt, @bind) = $sql->select($sql{table}, '*,unix_timestamp(timestamp) as epo', \%where, \'id DESC', $$ttvars{numvids}, $qpage * $$ttvars{numvids} - $$ttvars{numvids});
my $sth = $dbh->prepare($stmt);
$sth->execute(@bind);

$$ttvars{sql} = $sth->fetchall_arrayref({});
$sth->finish;

($stmt, @bind) = $sql->select($sql{table}, 'COUNT(*) as cnt', \%where);
$sth = $dbh->prepare($stmt);
$sth->execute(@bind);

my $stats = $sth->fetchall_arrayref({});
$sth->finish;
$$ttvars{totalvids} = $stats->[0]->{cnt};

mysql_disconnect();

if ($qdest && $qdest eq 'commands') {
   $$ttvars{title} = 'Bot Commands :: ' . $title;
   printheader();
   $tt->process('commands.tt', $ttvars) || croak($tt->error);
}
elsif ($qdest && $qdest eq 'contact') {
   $$ttvars{title} = 'Contact :: ' . $title;
   printheader();
   $tt->process('contact.tt', $ttvars) || croak($tt->error);
}
elsif ($qdest && $qdest eq 'categories') {
   $$ttvars{title} = 'Categories :: ' . $title;
   printheader();
   $$ttvars{categories} = \%categories;
   $tt->process('categories.tt', $ttvars) || croak($tt->error);
}
elsif ($qdest && $qdest eq 'info') {
   $$ttvars{title} = 'Info :: ' . $title;
   printheader();
   $tt->process('info.tt', $ttvars) || croak($tt->error);
}
else {
   for (@{$$ttvars{sql}}) {
      $_->{channel}   = encode_entities($_->{channel});
      $_->{vlength}   = duration($_->{vlength});
      $_->{vtitle}    = encode_entities($_->{vtitle});
      $_->{vuploader} = encode_entities($_->{vuploader}); 
      $_->{epo}       = duration(time - $_->{epo});
      $_->{width}     = 640;
      $_->{height}    = 360;
   }

   if ($qrss) {
      print header(
         -type          => 'application/rss+xml',
         -cache_control => 'no-cache, no-store, must-revalidate',
         -charset       => 'utf-8',
      );

      $tt->process('rss.tt', $ttvars) || croak($tt->error);
   }
   else {
      $$ttvars{pagecount} = ceil($$ttvars{totalvids}/$$ttvars{numvids});

      my $pageplusminus = 1;
      my @pages         = (1..$pageplusminus, $qpage-$pageplusminus..$qpage+$pageplusminus, ($$ttvars{pagecount}+1)-$pageplusminus..$$ttvars{pagecount});
      @pages = sort{ $a <=> $b } keys %{{ map { $_ => 1 } @pages }};

      while ($pages[0] < 1) {
         shift(@pages);
      }

      while ($pages[$#pages] > $$ttvars{pagecount}) {
         pop(@pages);
      }

      @pages = pairwise_walk { $a+1 == $b ? $b : ('..', $b) } @pages;

      $$ttvars{title}      = $title;
      $$ttvars{needjs}     = 1;
      $$ttvars{pages}      = \@pages;
      $$ttvars{categories} = \%categories;

      if ($debug) {
         use Data::Dumper;
         $$ttvars{debug} = Dumper($ttvars);
      }

      printheader();
      
      $tt->process('index.tt', $ttvars) || croak($tt->error);
   }
}
